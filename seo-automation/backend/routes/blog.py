"""Keyword-only HTML blog generation. No images."""

from __future__ import annotations

import asyncio
import html
import json
import random
import re
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_optional_user
from db import PageRecord, get_session
from services.post_owner import claim_slug

router = APIRouter()

_PLACEHOLDER = re.compile(
    r"belongs with the section above|teams evaluating|businesses comparing|"
    r"this section is about|keep the writing on|this is a structural example",
    re.I,
)
_CITY = re.compile(
    r"\b(san diego|los angeles|new york|chicago|houston|phoenix|dallas|austin|county)\b",
    re.I,
)

class BlogGenerateRequest(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=180)
    button_label: str = Field(default="", max_length=80)
    button_url: str = Field(default="", max_length=300)
    word_count: int = Field(default=800, ge=500, le=1000)
    keyword_length: str = Field(default="short", max_length=8)

class CountyPick(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    state: str = Field(..., min_length=2, max_length=40)

class CityPick(BaseModel):
    city: str = Field(..., min_length=2, max_length=80)
    state: str = Field(default="", max_length=40)
    state_name: str = Field(default="", max_length=40)
    county: str = Field(default="", max_length=80)

class BlogBatchRequest(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=180)
    state: str = Field(default="", max_length=40)
    county: str = Field(default="", max_length=80)
    counties: list[CountyPick] = Field(default_factory=list, max_length=40)
    cities: list[CityPick] = Field(default_factory=list, max_length=5000)
    count: int = Field(default=1, ge=1, le=5000)
    word_count: int = Field(default=800, ge=500, le=1000)

def _esc(text: str) -> str:
    return html.escape(re.sub(r"\s+", " ", (text or "").strip()))

def _short_lines(text: str) -> list[str]:
    """Keep each paragraph to 3 or 4 lines, then start the next one."""
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        return []
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()]
    if not sentences:
        return [clean]

    def lines(value: str) -> int:
        return max(1, (len(value) + 84) // 85)

    chunks: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        trial = " ".join(current + [sentence])
        if current and lines(trial) > 4:
            chunks.append(" ".join(current))
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


def _paras(text: str) -> str:
    raw_chunks = [c.strip() for c in re.split(r"\n{2,}", text or "") if c.strip()]
    if not raw_chunks and (text or "").strip():
        raw_chunks = [(text or "").strip()]
    chunks = []
    for chunk in raw_chunks:
        chunks.extend(_short_lines(chunk))
    return "\n".join(f"<p>{_link_contacts(_esc(c))}</p>" for c in chunks)


def _split_html_paragraphs(source: str) -> str:
    """Break a saved article the same way: 3 or 4 lines, then a new paragraph."""
    def repl(match: re.Match) -> str:
        open_tag, inner, close = match.group(1), match.group(2), match.group(3)
        if re.search(r"<(?!/?a\b)", inner, re.I):
            return match.group(0)
        plain = html.unescape(re.sub(r"<[^>]+>", " ", inner))
        parts = _short_lines(plain)
        if len(parts) <= 1:
            return match.group(0)
        return "\n".join(f"{open_tag}{_link_contacts(_esc(part))}{close}" for part in parts)

    return re.sub(r"(<p\b[^>]*>)(.*?)(</p>)", repl, source or "", flags=re.I | re.S)

def _link_contacts(text: str) -> str:
    text = text.replace("(619) 724-9517", '<a href="tel:+16197249517">(619) 724-9517</a>')
    text = re.sub(
        r'(?<![\w./@-])zeorbit\.com',
        '<a href="https://zeorbit.com">zeorbit.com</a>',
        text,
        flags=re.I,
    )
    return text

def _title_case(text: str) -> str:
    small = {"a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "at", "by", "with", "from"}
    words = re.sub(r"\s+", " ", text or "").strip().split(" ")
    out = []
    for index, word in enumerate(words):
        core = word.strip("?:.,")
        if index and core.lower() in small:
            out.append(word.lower())
        elif core:
            out.append(word[:1].upper() + word[1:])
        else:
            out.append(word)
    return " ".join(out)

def _is_query(keyword: str) -> bool:
    return bool(
        re.match(r"^(who|what|which|how|where|why)\b", (keyword or "").strip(), flags=re.I)
        or re.search(r"\bnear me\b", keyword or "", flags=re.I)
    )

def _slug(text: str) -> str:
    raw = re.sub(r"^https?://[^/]+", "", (text or "").strip(), flags=re.I)
    raw = raw.strip("/")
    raw = re.sub(r"^blog/", "", raw, flags=re.I)
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    if slug == "blog":
        slug = ""
    elif slug.startswith("blog-"):
        slug = slug[5:]
    return slug[:80] or "article"

def _items(value) -> list[str]:
    if isinstance(value, str):
        return [line.strip(" -•\t") for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []

_PHONE = "(619) 724-9517"
_EMAIL = "info@zeorbit.com"
_ADDRESS = "4231 Balboa Avenue, Suite 1340, San Diego, CA 92117"
_CONTACT_PAGE = "https://zeorbit.com/contact"
_ICON_PHONE = '<svg class="reach-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" style="fill:currentColor;"><path d="M6.5 3.5h3l1.5 4-2 1.2a12 12 0 0 0 5.3 5.3l1.2-2 4 1.5v3A2 2 0 0 1 17.5 18 14.5 14.5 0 0 1 6 6.5 2 2 0 0 1 6.5 3.5z"/></svg>'
_ICON_MAIL = '<svg class="reach-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:1.6;"><path d="M3 6h18v12H3z"/><path d="m3 7 9 7 9-7"/></svg>'
_ICON_PIN = '<svg class="reach-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.2"/></svg>'

def _build_html(data: dict) -> str:
    image = str(data.get("image_url") or "").strip()
    image_alt = _esc(data.get("image_alt") or data.get("title") or "")
    parts = [f'<h1 style="font-weight:700;">{_esc(data.get("title") or "")}</h1>']
    if image:
        parts.append(f'<img class="blog-hero" src="{_esc(image)}" alt="{image_alt}">')
    parts.append(_paras(data.get("introduction") or ""))
    process = str(data.get("process_heading") or data.get("keyword") or "The practical steps").strip()
    process = re.sub(r"\[[^\]]*\]", "", process).strip()
    if re.search(r"follow this process|^scene\b|^what changes$", process, re.I) or not process:
        process = ""
    seed_now = str(data.get("keyword") or "")
    if _is_query(seed_now) and process.lower().rstrip("?.") == seed_now.lower().rstrip("?."):
        labels = (
            "How To Read This Answer",
            "What To Check First",
            "Signs The Studio Fits",
            "What The Page Should Prove",
            "Before You Call",
        )
        process = labels[sum(ord(char) for char in seed_now.lower()) % len(labels)]
    process = "" if data.get("_outline") else _title_case(process)
    title_now = str(data.get("title") or "")
    folded = process.lower().rstrip("?.")
    title_folded = title_now.lower()
    keyword_folded = seed_now.lower().strip()
    repeats_title = (
        not folded
        or folded == keyword_folded
        or folded == title_folded.rstrip("?.")
        or (folded and folded in title_folded)
        or (keyword_folded and keyword_folded in folded and len(folded) <= len(keyword_folded) + 4)
    )
    steps = [s for s in (data.get("steps") or []) if isinstance(s, dict)]
    layout = str(data.get("layout") or "1")
    avoid = data.get("_avoid_images") or set()
    if not isinstance(avoid, set):
        avoid = set(avoid)
    seed = str(data.get("keyword") or data.get("title") or "website")
    parts.extend(_layout_html(layout, "" if repeats_title else process, steps, seed, avoid, data, skip_first_image=bool(image)))
    parts.append(_faq_html(seed_now, data.get("faqs")))
    reach = str(data.get("reach_heading") or "Talk with the team").strip()
    if re.search(r"contact us", reach, re.I):
        reach = "Talk with the team"
    lines = _items(data.get("reach_lines"))[:2]
    label = str(data.get("button_label") or data.get("cta") or "Start the brief").strip()
    catchy = ("Start the brief", "Get the plan", "Map the build", "Share the idea", "See the next step")
    if re.search(r"fill(\s+the)?\s+form|contact us|get in touch|send message|submit", label, re.I) or not label:
        label = catchy[sum(ord(c) for c in (layout + label)) % len(catchy)]
    from services.public_page_service import _vcard_html

    button_url = str(data.get("button_url") or "").strip()
    if not re.match(r"^https://[^\s]+$", button_url):
        button_url = "https://zeorbit.com/contact"
    parts.append(_vcard_html(
        str(data.get("title") or data.get("keyword") or ""),
        label,
        button_url,
    ))
    return _only_opening_image("\n".join(p for p in parts if p))

def _only_opening_image(html: str) -> str:
    """Keep the title photo. Drop later photos, stylesheet dumps, and the generic closer."""
    html = re.sub(r"<style[\s\S]*?</style>", "", html or "", flags=re.I)
    html = re.sub(
        r"<section[^>]*>\s*<h2[^>]*>\s*(How To Use This Page|What A Visitor Should Understand|What This Answer Should Include|What To Compare)\s*</h2>[\s\S]*?</section>",
        "",
        html,
        flags=re.I,
    )

    def _keep_image(match: re.Match) -> str:
        tag = match.group(0)
        if "blog-hero" in tag or "zeorbit-logo" in tag:
            return tag
        return ""

    return re.sub(r"<img\b[^>]*>", _keep_image, html, flags=re.I)

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
_CARD_CLASS = ("blog-reach", "zo-vcard")
_SKIP_CLASS = _CARD_CLASS + ("zo-site-footer", "zo-host-header")

def _norm_heading(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip().lower()
    return text.strip(" .:?")

class _Markup(HTMLParser):
    """One parser for headings, visible words, images, links, and skipped regions."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1_texts: list[str] = []
        self.h2_texts: list[str] = []
        self.h3_texts: list[str] = []
        self.paragraphs = 0
        self.images: list[str] = []
        self.bad_alt = False
        self.bad_link = False
        self.malformed = False
        self.cards = 0
        self.visible: list[str] = []
        self._stack: list[tuple[str, bool, bool]] = []
        self._heading: tuple[str, list[str]] | None = None
        self._para: list[str] | None = None

    def _skipped(self) -> bool:
        return bool(self._stack and self._stack[-1][1])

    def handle_starttag(self, tag, attrs):
        self._open(tag.lower(), attrs, void=False)

    def handle_startendtag(self, tag, attrs):
        self._open(tag.lower(), attrs, void=True)

    def _open(self, tag, attrs, void=False):
        attrs = dict(attrs or [])
        cls = f"{attrs.get('class') or ''} {attrs.get('id') or ''}"
        style = (attrs.get("style") or "").replace(" ", "").lower()
        hidden = "hidden" in attrs or "display:none" in style
        is_card = any(name in cls for name in _CARD_CLASS)
        skip = self._skipped() or hidden or tag in {"script", "style", "nav"} or any(name in cls for name in _SKIP_CLASS)
        if is_card:
            self.cards += 1
        if tag not in _VOID and not void:
            self._stack.append((tag, skip, is_card))
        if skip:
            return
        if tag in {"h1", "h2", "h3"}:
            self._heading = (tag, [])
            return
        if tag == "p":
            self._para = []
            return
        if tag == "img":
            alt = (attrs.get("alt") or "").strip()
            self.images.append(alt)
            if not alt and "zeorbit-logo" not in (attrs.get("class") or ""):
                self.bad_alt = True
            return
        if tag == "a":
            href = (attrs.get("href") or "").strip()
            if href and not re.match(r"^(https?:|mailto:|tel:|#|/)", href, re.I):
                self.bad_link = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        skipped = self._skipped()
        if self._heading and tag == self._heading[0] and not skipped:
            text = re.sub(r"\s+", " ", "".join(self._heading[1])).strip()
            {"h1": self.h1_texts, "h2": self.h2_texts, "h3": self.h3_texts}[tag].append(text)
            self._heading = None
        if self._para is not None and tag == "p" and not skipped:
            if re.search(r"[A-Za-z0-9]", "".join(self._para)):
                self.paragraphs += 1
            self._para = None
        if not self._stack:
            self.malformed = True
            return
        if self._stack[-1][0] == tag:
            self._stack.pop()
            return
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                self.malformed = True
                del self._stack[index:]
                return
        self.malformed = True

    def handle_data(self, data):
        if self._skipped() or not data:
            return
        if self._heading is not None:
            self._heading[1].append(data)
        if self._para is not None:
            self._para.append(data)
        self.visible.append(data)

    def close(self):
        super().close()
        if self._heading is not None or self._stack:
            self.malformed = True

def _article_words(content_html: str) -> int:
    """Visible article words only. Cards, navigation, scripts, styles, alt text, and URLs are excluded."""
    parser = _Markup()
    try:
        parser.feed(content_html or "")
        parser.close()
    except Exception:
        return 0
    text = re.sub(r"https?://\S+", " ", " ".join(parser.visible))
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", text))

_UNFINISHED = {"and", "or", "with", "into", "for", "to", "of", "your", "the", "a", "an", "in", "on", "by", "from", "that", "this"}


def _finished_phrase(text: str) -> str:
    words = re.sub(r"\s+", " ", text or "").strip(" .|:-").split()
    while words and words[-1].lower().strip(".,") in _UNFINISHED:
        words.pop()
    return " ".join(words)


def _fit_title(keyword: str, tagline: str = "") -> str:
    """A title stays under 60 characters and never stops in the middle of a phrase."""
    shown = _finished_phrase(_pretty_keyword(re.sub(r"\s+", " ", keyword or "").strip(" ?. ") or "Article")) or "Article"
    tagline = _finished_phrase(tagline)
    if tagline and shown.lower() in tagline.lower():
        tagline = _finished_phrase(" ".join(word for word in tagline.split() if word.lower() not in {part.lower() for part in shown.split()}))
    full = f"{shown} | {tagline}" if tagline else shown
    title = full if len(full) <= 60 else shown
    while len(title) > 60 and " " in title:
        title = _finished_phrase(title.rsplit(" ", 1)[0])
    title = _finished_phrase(title)
    if len(title) > 60:
        title = _finished_phrase(title[:60].rsplit(" ", 1)[0])
    return title or "Article"

def _fit_meta(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return ""
    if len(text) <= 160:
        return text
    window = text[:160]
    sentence = max(window.rfind("."), window.rfind("!"), window.rfind("?"))
    if sentence >= 80:
        cut = window[: sentence + 1]
    else:
        cut = window.rsplit(" ", 1)[0] if " " in window else window[:160]
    cut = cut.rstrip(" ,;:-|").strip()
    if not cut:
        cut = text[:160].rsplit(" ", 1)[0].strip() or text[:160]
    return cut[:160]

def _problems(content_html: str, keyword: str, word_target: int = 800) -> list[str]:
    problems = []
    parser = _Markup()
    try:
        parser.feed(content_html or "")
        parser.close()
    except Exception:
        return ["malformed HTML"]
    if any(item[2] for item in parser._stack):
        problems.append("the contact card is not closed")
    if parser.malformed and "the contact card is not closed" not in problems:
        problems.append("malformed HTML")
    valid_h1 = [text for text in parser.h1_texts if _norm_heading(text)]
    if len(valid_h1) != 1:
        problems.append("the article needs exactly one H1")
    section_heads = [_norm_heading(text) for text in parser.h2_texts + parser.h3_texts]
    filled = [text for text in section_heads if text]
    if len(filled) < 2:
        problems.append("not enough sections")
    if any(not _norm_heading(text) for text in parser.h1_texts + parser.h2_texts + parser.h3_texts):
        problems.append("empty section")
    if len(filled) != len(set(filled)):
        problems.append("duplicate headings")
    if parser.paragraphs < 3:
        problems.append("the body paragraphs are missing")
    if parser.cards < 1:
        problems.append("the closing note is missing")
    if "##" in (content_html or "") or "```" in (content_html or ""):
        problems.append("markdown leaked into the HTML")
    visible = " ".join(parser.visible)
    if _PLACEHOLDER.search(visible):
        problems.append("placeholder text")
    if " in " not in (keyword or "").lower() and _CITY.search(visible) and not _CITY.search(keyword):
        problems.append("unsupported location")
    if len(parser.images) < 1:
        problems.append("the article needs one image")
    if parser.bad_alt:
        problems.append("an image is missing alt text")
    if parser.bad_link:
        problems.append("a link is malformed")
    if re.search(r"\$\s?\d|\b\d+\s+(hours|days|weeks|months)\b", visible, re.I) and not re.search(r"\$\s?\d|cost|price", keyword or "", re.I):
        problems.append("the article invented a number")
    floor = int(int(word_target or 800) * 0.9) if int(word_target or 800) >= 500 else 40
    if _article_words(content_html or "") < floor:
        problems.append("article is too short")
    return problems

_USED_PATH = Path(__file__).with_name("used_layouts.json")
_USED_IMAGES_PATH = Path(__file__).with_name("used_blog_images.json")

def _read_used() -> list[str]:
    try:
        saved = json.loads(_USED_PATH.read_text())
        if isinstance(saved, list):
            return [str(name) for name in saved if str(name).strip()]
    except (OSError, json.JSONDecodeError):
        return []
    return []

def _reserve_layout() -> str:
    """Take the next layout number and store it so it cannot be selected again."""
    used = _read_used()
    numbers = [int(name) for name in used if str(name).isdigit()]
    layout_id = str(max(numbers, default=0) + 1)
    used.append(layout_id)
    _USED_PATH.write_text(json.dumps(used))
    return layout_id

def _without_unknown_cities(text: str, keyword: str) -> str:
    if _CITY.search(keyword or ""):
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text or "")
    kept = [sentence for sentence in sentences if sentence and not _CITY.search(sentence)]
    return " ".join(kept).strip() or text

def _plain_field(value) -> str:
    if isinstance(value, dict):
        return str(value.get("body") or value.get("text") or value.get("title") or "").strip()
    text = str(value or "").strip()
    if text.startswith("{") or text.startswith("["):
        return ""
    return text

def _clean_steps(steps: list) -> list[tuple[str, str]]:
    cleaned = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        title = _plain_field(
            step.get("title") or step.get("heading") or step.get("phase")
            or step.get("action") or step.get("name") or step.get("label")
        )
        body = _plain_field(step.get("body") or step.get("text") or step.get("description") or step.get("content"))
        title = re.sub(r"^scene\s*\d+\s*:\s*", "", title, flags=re.I).strip()
        title = re.sub(r"^\[|\]$", "", title).strip()
        if re.fullmatch(r"\[?\s*\]?", title):
            continue
        if title and body.lower().startswith(title.lower()):
            body = body[len(title):].lstrip(" .:-—")
        if title and not body:
            body = f"{title} is a concrete part of the work, written so a reader knows what to do next."
        if title and body:
            cleaned.append((title if re.search(r"[a-z]", title) and re.search(r"[A-Z]", title) else _title_case(title), body))
    return cleaned

_PATTERNS = ("cards", "timeline", "split", "faq", "table", "poster", "checklist", "magazine")

def _pattern_name(layout: str) -> str:
    number = max(int(layout) if str(layout).isdigit() else 1, 1) - 1
    return _PATTERNS[number % len(_PATTERNS)]

def _layout_html(layout: str, process: str, steps: list, seed: str, avoid: set[str] | None = None, data: dict | None = None, skip_first_image: bool = False) -> list[str]:
    """One article shape for every template id. Dark text, stacked sections, no repeated steps."""
    rows = _clean_steps(steps)
    pattern = "article"
    items = []
    for index, (title, body) in enumerate(rows):
        img = ""
        prose, bullets = [], []
        for line in str(body).split("\n"):
            line = line.strip()
            if line.startswith("- "):
                bullets.append(line[2:].strip())
            elif line:
                prose.append(line)
        list_html = "<ul style=\"margin:10px 0 0;padding-left:18px;color:#3c4650;line-height:1.6;\">" + "".join(f"<li>{_esc(item)}</li>" for item in bullets) + "</ul>" if bullets else ""
        prose_html = "".join(f'<p style="margin:0 0 8px;color:#3c4650;line-height:1.6;font-weight:400;">{_esc(part)}</p>' for part in prose)
        items.append(
            '<section style="margin:0 0 18px;padding:0 0 18px;border-bottom:1px solid #eceff2;">'
            f'{img}<h2 style="margin:0 0 8px;color:#14181d;font-size:22px;font-weight:700;">{_esc(title)}</h2>'
            f"{prose_html}{list_html}</section>"
        )
    heading = f'<h2 style="margin:8px 0 16px;color:#14181d;">{_esc(process)}</h2>' if process else ""
    html = (
        f'<div class="blog-layout" data-layout="{_esc(layout)}" data-pattern="{pattern}" style="color:#14181d;">'
        f"{heading}{''.join(items)}"
        f"</div>"
    )
    return [html]

def _image_pool(seed: str) -> list[str]:
    from services.image_service import _WEB_DESIGN_IMAGES, _curated_pool_for_topic, _with_unsplash_params

    pool = _curated_pool_for_topic(seed) or list(_WEB_DESIGN_IMAGES)
    return [_with_unsplash_params(url) for url in pool]

def _read_used_images() -> list[str]:
    try:
        saved = json.loads(_USED_IMAGES_PATH.read_text())
        if isinstance(saved, list):
            return [str(url) for url in saved if str(url).strip()]
    except (OSError, json.JSONDecodeError):
        return []
    return []

def _pick_images(seed: str, count: int, avoid: set[str] | None = None) -> list[str]:
    from services.image_service import _WEB_DESIGN_IMAGES, _with_unsplash_params, normalize_image_key

    topic_pool = _image_pool(seed)
    web_pool = [_with_unsplash_params(url) for url in _WEB_DESIGN_IMAGES]
    # Topic photos first, then the web library. Food and other niches stay out.
    raw = list(dict.fromkeys([*topic_pool, *web_pool]))
    pool = []
    seen = set()
    for url in raw:
        key = normalize_image_key(url)
        if not key or key in seen:
            continue
        seen.add(key)
        pool.append(url)
    if not pool or count < 1:
        return []
    history = _read_used_images()
    recent_keys = set()
    for url in history[-len(pool):]:
        key = normalize_image_key(url)
        if key:
            recent_keys.add(key)
    avoid_keys = {normalize_image_key(url) for url in (avoid or ()) if normalize_image_key(url)}
    start = 0
    if history:
        last = normalize_image_key(history[-1])
        for index, url in enumerate(pool):
            if normalize_image_key(url) == last:
                start = (index + 1) % len(pool)
                break
    picked = []
    picked_keys = set()

    def consider(url: str, skip_recent: bool) -> None:
        key = normalize_image_key(url)
        if not key or key in picked_keys or key in avoid_keys:
            return
        if skip_recent and key in recent_keys:
            return
        picked.append(url)
        picked_keys.add(key)

    for offset in range(len(pool)):
        if len(picked) >= count:
            break
        consider(pool[(start + offset) % len(pool)], True)
    if len(picked) < count:
        for offset in range(len(pool)):
            if len(picked) >= count:
                break
            consider(pool[(start + offset) % len(pool)], False)
    if picked:
        history.extend(picked)
        _USED_IMAGES_PATH.write_text(json.dumps(history[-4000:]))
    return picked

def _featured_image(keyword: str, title: str) -> tuple[str, str]:
    text = f"{keyword} {title}".lower()
    if "wordpress" in text:
        return "https://zeorbit.com/banners/wordpress-website-design-card.png", title or keyword
    if "microsoft" in text or "365" in text or "outlook" in text:
        return "https://zeorbit.com/banners/microsoft-365-card.png", title or keyword
    shots = _pick_images(keyword or title, 1)
    return (shots[0] if shots else ""), title or keyword

def _faq_html(keyword: str, faqs=None) -> str:
    """Three questions. Use the ones written for this keyword when they exist."""
    pick = []
    for item in faqs or []:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or item.get("title") or "").strip()
        answer = str(item.get("answer") or item.get("body") or "").strip()
        if question and answer:
            pick.append((question, answer))
        if len(pick) == 3:
            break
    if len(pick) < 3:
        shown = _as_noun(keyword)
        named = _sentence_noun(keyword)
        pick = [
            (f"What does {shown} include?", "The work includes the main deliverable and the parts required to use the finished work. The list is agreed before the work starts."),
            ("Who is this for?", "It is for a client who wants the scope named before the work starts."),
            ("What should you compare before hiring?", "Compare finished examples, what the plan includes, and who supports the work after delivery."),
        ]
    blocks = []
    for index, (question, answer) in enumerate(pick, start=1):
        blocks.append(
            f'<h3 style="margin:14px 0 6px;color:#14181d;font-size:17px;font-weight:700;">{index}. {_esc(question)}</h3>'
            f'<p style="margin:0 0 8px;color:#3c4650;line-height:1.6;font-weight:400;">{_esc(answer)}</p>'
        )
    return (
        '<section class="blog-faq" style="margin:8px 0 22px;">'
        '<h2 style="margin:0 0 8px;color:#14181d;font-size:22px;font-weight:700;">Frequently Asked Questions</h2>'
        + "".join(blocks)
        + "</section>"
    )

def _work_kind(blob: str) -> str:
    if re.search(r"video|film|videograph|photo", blob):
        return "video"
    if re.search(r"\bseo\b|search engine", blob):
        return "seo"
    if re.search(r"e-?commerce|shopify|online store", blob):
        return "store"
    if re.search(r"flutter|react native|\bapp\b|android|\bios\b|mobile app", blob):
        return "app"
    if re.search(r"web|website|design|developer", blob):
        return "web"
    return "general"

def _pretty_keyword(raw: str) -> str:
    small = {"a", "an", "the", "in", "on", "for", "of", "and", "to", "near", "with", "at", "by"}
    words = raw.split()
    shown = []
    for index, word in enumerate(words):
        if index and word.lower() in small:
            shown.append(word.lower())
        else:
            shown.append(word[:1].upper() + word[1:])
    return " ".join(shown)

def _article_a(shown: str) -> str:
    if re.match(r"^(a|an|the)\b", shown, flags=re.I):
        return shown
    return ("an " if shown[:1].lower() in "aeiou" else "a ") + shown

def _topic_lines(blob: str) -> tuple[tuple[str, ...], str, str]:
    """Taglines, opening scene, and the sentence that names the keyword."""
    if re.search(r"video|film|videograph|photo", blob):
        return (
            ("Capture Every Moment That Matters", "Keep the Sessions on Record", "Save the Day in Clear Footage", "Turn the Event into Footage"),
            "A successful gathering brings people together to share ideas and decisions. Recording those moments keeps the talks, announcements, and room available after everyone leaves.",
            "helps the important sessions, speakers, and activities get documented with clear picture and sound.",
        )
    if re.search(r"\bseo\b|search engine", blob):
        return (
            ("Pages People Can Actually Find", "Search That Matches the Offer", "Get the Right Pages Found", "Be Clear Before You Rank"),
            "People search with a job in mind, then open the page that explains it plainly. The wording, the title, and the page they land on have to match that search.",
            "helps the right pages get written, titled, and checked so the offer is what shows up.",
        )
    if re.search(r"e-?commerce|shopify|online store", blob):
        return (
            ("A Store People Can Finish", "Products, Prices, and Checkout", "Sell Without the Extra Steps", "From Catalog to Checkout"),
            "A store has to show the product, the price, and a way to pay. If any of those is hard to find, the visit ends before the order.",
            "covers the catalog, the checkout, and a layout that still works on a phone.",
        )
    if re.search(r"\bapp\b|android|ios|mobile app", blob):
        return (
            ("One Job, Done on a Phone", "The First Version That Works", "From Idea to a Working App", "Build the Path People Finish"),
            "An app is useful when someone can finish one job without hunting through screens. The first version should prove that path before extra features are added.",
            "covers the first screen a person must finish, the accounts that screen needs, and a build for iPhone and Android.",
        )
    if re.search(r"web|website|design|developer", blob):
        return (
            ("A Site That Explains the Offer", "Clear Pages, Clear Next Step", "Built for the First Visit", "Design People Can Finish"),
            "A website has one job on the first visit: say what you do, who it is for, and what to do next. Extra pages only help after that is obvious.",
            "covers the structure, the design, and a mobile layout that still leads to contact.",
        )
    return (
        ("What to Know Before You Start", "A Clear Plan for the Work", "Done With the Details in Place", "Make the Scope Obvious"),
        "The useful version of this work names the result, who it is for, and what finished looks like. Vague scope is what makes the page hard to trust.",
        "covers that result, the pieces around it, and a plan you can review before the work starts.",
    )

def _keyword_title(keyword: str) -> str:
    """Keyword first, then a line that fits the topic. Same shape as a published post title."""
    raw = re.sub(r"\s+", " ", keyword or "").strip(" ?.") or "website design"
    shown = _pretty_keyword(raw)
    lines, _scene, _tail = _topic_lines(raw.lower())
    return f"{shown} | {random.choice(lines)}"

def _lead_copy(keyword: str) -> tuple[str, str]:
    """Two opening paragraphs plus a short description, both about this keyword."""
    raw = re.sub(r"\s+", " ", keyword or "").strip(" ?.") or "website design"
    shown = _pretty_keyword(raw)
    _lines, scene, tail = _topic_lines(raw.lower())
    if re.search(r"videograph|photographer|designer|developer|consultant", raw, flags=re.I) and not re.search(r"development|design\b|company|service", raw, flags=re.I):
        named = _article_a(shown)
        second = f"Hiring {named} {tail}"
    else:
        second = f"{shown} {tail}"
    intro = f"{scene}\n\n{second}"
    meta = f"{shown} {tail}"
    if len(meta) > 160:
        meta = meta[:157].rsplit(" ", 1)[0]
    return intro, meta

def _strip_invented_claims(html: str, keyword: str) -> str:
    """Remove sentences that invent a duration, unless the keyword is about time or price."""
    if re.search(r"\b(cost|price|how long|timeline|duration)\b", keyword or "", re.I):
        return html or ""
    invented = re.compile(
        r"\b(?:a few|several|a couple of|\d+)\s+(?:hours|days|weeks|months|years)\b",
        re.I,
    )

    def _paragraph(match: re.Match) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", match.group(2))
        kept = [sentence.strip() for sentence in sentences if sentence.strip() and not invented.search(sentence)]
        text = " ".join(kept).strip()
        if not text:
            return ""
        return match.group(1) + text + match.group(3)

    def _place(match: re.Match) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", match.group(2))
        kept = []
        for sentence in sentences:
            named = _CITY.findall(sentence)
            if any(city.lower() not in (keyword or "").lower() for city in named):
                continue
            kept.append(sentence.strip())
        text = " ".join(part for part in kept if part).strip()
        if not text:
            return ""
        return match.group(1) + text + match.group(3)

    html = re.sub(r"(<p\b[^>]*>)(.*?)(</p>)", _paragraph, html or "", flags=re.I | re.S)
    html = re.sub(r"(<p\b[^>]*>)(.*?)(</p>)", _place, html, flags=re.I | re.S)
    html = re.sub(
        r"<h3\b[^>]*>[^<]*\bhow long\b[^<]*</h3>\s*(?:<p\b[^>]*>[\s\S]*?</p>)?",
        "",
        html,
        flags=re.I,
    )
    from services.public_page_service import ensure_three_faqs
    return ensure_three_faqs(html)


def _keyword_forms(keyword: str) -> list[str]:
    forms = []
    for raw in (keyword, _pretty_keyword(keyword), _as_noun(keyword), _sentence_noun(keyword)):
        cleaned = re.sub(r"\s+", " ", raw or "").strip(" ?.")
        cleaned = re.sub(r"^(a|an)\s+", "", cleaned, flags=re.I)
        if not cleaned:
            continue
        if cleaned.lower() not in {item.lower() for item in forms}:
            forms.append(cleaned)
    forms.sort(key=len, reverse=True)
    return forms


def _limit_keyword_text(text: str, forms: list[str], budget: list[int], limit: int = 6) -> str:
    """Keep the full keyword in a few sentences. Later copies become ordinary wording."""
    if not text or not forms:
        return text
    pattern = re.compile("|".join(re.escape(form) for form in forms), flags=re.I)

    def replace(match: re.Match) -> str:
        if budget[0] < limit:
            budget[0] += 1
            return match.group(0)
        return "this work" if match.group(0)[:1].islower() else "This work"

    return pattern.sub(replace, text)


def _limit_keyword_draft(data: dict, keyword: str) -> dict:
    forms = _keyword_forms(keyword)
    budget = [0]
    data = {**data}
    data["introduction"] = _limit_keyword_text(str(data.get("introduction") or ""), forms, budget)
    steps = []
    for step in data.get("steps") or []:
        if not isinstance(step, dict):
            steps.append(step)
            continue
        steps.append({
            **step,
            "title": _limit_keyword_text(str(step.get("title") or ""), forms, budget),
            "body": _limit_keyword_text(str(step.get("body") or ""), forms, budget),
        })
    data["steps"] = steps
    faqs = []
    for item in data.get("faqs") or []:
        if not isinstance(item, dict):
            faqs.append(item)
            continue
        faqs.append({
            **item,
            "question": _limit_keyword_text(str(item.get("question") or ""), forms, budget),
            "answer": _limit_keyword_text(str(item.get("answer") or ""), forms, budget),
        })
    data["faqs"] = faqs
    return data


def _cap_keyword_html(html: str, keyword: str, limit: int = 6) -> str:
    """The full keyword may appear at most six times in the finished article."""
    forms = _keyword_forms(keyword)
    if not html or not forms:
        return html or ""
    pattern = re.compile(
        "|".join(rf"\b{re.escape(form)}\b" for form in forms),
        flags=re.I,
    )
    budget = [0]

    def replace(match: re.Match) -> str:
        if budget[0] < limit:
            budget[0] += 1
            return match.group(0)
        return "this work" if match.group(0)[:1].islower() else "This work"

    parts = re.split(r"(<[^>]+>)", html)
    capped = []
    for part in parts:
        capped.append(part if part.startswith("<") else pattern.sub(replace, part))
    return "".join(capped)


def _balance_keyword(html: str, keyword: str) -> str:
    """Drop the repeated filler lines, then keep the keyword to six uses."""
    html = re.sub(
        r"<p>[^<]*is part of the work described on this page\.</p>",
        "",
        html or "",
        flags=re.I,
    )
    return _cap_keyword_html(html, keyword, 6)

def _pack(data: dict, keyword: str, button_label: str = "", button_url: str = "", layout: str = "") -> dict:
    tagline = re.sub(r"\s+", " ", str(data.get("tagline") or "")).strip(" .")
    model_title = re.sub(r"\s+", " ", str(data.get("title") or "")).strip()
    if data.get("_from_model") and model_title and keyword.lower().split()[0] in model_title.lower() and "|" in model_title:
        title = _fit_title(keyword, model_title.split("|", 1)[-1])
    else:
        title = _fit_title(keyword, tagline if data.get("_from_model") else "")
        if not tagline or not data.get("_from_model"):
            title = _fit_title(keyword, tagline or _keyword_title(keyword).split("|", 1)[-1])
    _lead, meta = _lead_copy(keyword)
    if data.get("_from_model"):
        model_intro = str(data.get("introduction") or "").strip()
        if len(model_intro.split()) >= 8:
            _lead = model_intro
        supplied = re.sub(r"\s+", " ", str(data.get("meta_description") or "")).strip()
        source = supplied if len(supplied) >= 80 else re.sub(r"\s+", " ", model_intro.replace("\n", " "))
        meta = _fit_meta(source or meta)
    else:
        meta = _fit_meta(meta)
    slug = _slug(keyword) or _slug(str(data.get("slug") or "")) or _slug(title)
    image_url, image_alt = _featured_image(keyword, title)
    data = {**data, "_avoid_images": {image_url} if image_url else set()}
    steps = [
        {**step, "body": _without_unknown_cities(str(step.get("body") or ""), keyword)}
        if isinstance(step, dict) else step
        for step in (data.get("steps") or [])
    ]
    ready = [step for step in steps if isinstance(step, dict) and str(step.get("title") or "").strip() and str(step.get("body") or "").strip()]
    generic = {"what the work covers", "how the work is checked", "how to compare options"}
    current = [str(step.get("title") or "").strip().lower() for step in ready]
    if not data.get("_from_model") or len(ready) < 3 or set(current) == generic:
        raise RuntimeError("The writer is busy. Generate this post again.")
    steps = ready[:3]
    data["_outline"] = True
    if _is_query(keyword):
        asked = _pretty_keyword(keyword).rstrip(".")
        title = asked if asked.endswith("?") else asked + "?"
        if len(title) > 60:
            title = title[:59].rstrip(" |:-") + "?"
    seo_title = title
    introduction = _lead
    data = _limit_keyword_draft({
        **data,
        "introduction": introduction,
        "steps": steps,
    }, keyword)
    content_html = _balance_keyword(_build_html({
        **data,
        "keyword": keyword,
        "layout": layout,
        "title": title,
        "image_url": image_url,
        "image_alt": image_alt,
        "button_label": button_label,
        "button_url": button_url,
    }), keyword)
    related = [str(k).strip() for k in (data.get("related_keywords") or []) if str(k).strip()][:8]
    return {
        "keyword": keyword,
        "detected_industry": str(data.get("detected_industry") or "").strip(),
        "detected_audience": str(data.get("detected_audience") or "").strip(),
        "search_intent": str(data.get("search_intent") or "informational").strip().lower(),
        "title": title,
        "seo_title": seo_title,
        "meta_description": meta,
        "slug": slug,
        "primary_keyword": keyword,
        "related_keywords": related,
        "content_html": content_html,
        "word_count": _article_words(content_html),
        "layout": layout,
        "pattern": _pattern_name(layout) if layout else "",
        "image_url": image_url,
        "image_alt": image_alt,
        "button_label": button_label or str(data.get("cta") or "Get in touch").strip(),
        "button_url": button_url,
    }

async def _groq_json(prompt: str, max_tokens: int = 2800, model: str = "", timeout: float = 12) -> dict | None:
    """Use a small non-reasoning Groq model. The default reasoning model spends the free token budget before it emits JSON."""
    import httpx
    from config import settings
    from services.llm_service import _extract_json

    if not (settings.GROQ_API_KEY or "").strip():
        return None
    if not model:
        model = settings.GROQ_MODEL or "openai/gpt-oss-20b"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt + "\nReturn JSON only. No markdown fences."}],
        "temperature": 0.4,
        "max_tokens": max_tokens,
        "include_reasoning": False,
        "reasoning_effort": "low",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json=payload,
            )
        if resp.status_code == 429:
            wait = 20
            match = re.search(r"try again in ([0-9.]+)s", resp.text or "")
            if match:
                wait = min(45, float(match.group(1)) + 1)
            print(f"[blog] groq rate limited, wait {wait}s")
            return {"__rate_limited": True, "__wait": wait}
        if resp.status_code != 200:
            print(f"[blog] groq {resp.status_code}: {resp.text[:160]}")
            return None
        message = resp.json()["choices"][0]["message"]
        text = message.get("content") or message.get("reasoning") or ""
        return _extract_json(text)
    except Exception as e:
        print(f"[blog] groq llama error: {e}")
        return None

async def _expand_to_length(data: dict, keyword: str, word_count: int) -> dict:
    """Add a short passage only when the article is under the 800 to 900 word range."""
    html = str(data.get("content_html") or "")
    target = min(900, max(800, int(word_count or 850)))
    low = 800
    high = 900
    added: list[str] = []
    for _ in range(1):
        current = _article_words(html)
        if current >= low:
            break
        ask = min(120, max(40, target - current))
        extra = await _groq_json(
            (
                f"The keyword is {keyword}. Write about {ask} words of new paragraphs a buyer of this service can use. "
                "Stay on this keyword. Do not repeat a sentence you were not given. "
                "Do not invent prices, rankings, statistics, or cities that are not in the keyword. "
                "Do not add a heading. Separate paragraphs with a blank line. "
                'Return JSON {"body":"the paragraphs"}'
            ),
            max_tokens=900,
            timeout=18,
        )
        body = str((extra or {}).get("body") or "") if isinstance(extra, dict) and not extra.get("__rate_limited") else ""
        if len(body.split()) < 40:
            try:
                from services.llm_service import chat_json
                backup = await chat_json(
                    (
                        f"The keyword is {keyword}. Write about {ask} words of new paragraphs a buyer can use. "
                        "Stay on this keyword. Do not invent prices, rankings, statistics, or cities that are not in the keyword. "
                        "Do not add a heading. Separate paragraphs with a blank line. "
                        'Return JSON {"body":"the paragraphs"}'
                    ),
                    temperature=0.3,
                    max_tokens=900,
                    provider="gemini",
                )
                body = str((backup or {}).get("body") or "")
            except Exception as exc:
                print(f"[blog] expand backup failed for {keyword}: {exc}")
        if len(body.split()) < 40:
            print(f"[blog] expand skipped for {keyword}: short model reply")
            break
        chunk = _paras(body)
        if not chunk or chunk in html:
            break
        added.append(chunk)
        if 'class="blog-faq"' in html:
            html = html.replace('<section class="blog-faq"', chunk + '<section class="blog-faq"', 1)
        else:
            html += "\n" + chunk
    while added and _article_words(html) > high:
        html = html.replace(added.pop(), "", 1)
    data["content_html"] = html
    data["word_count"] = _article_words(html)
    print(f"[blog] words {data['word_count']} target {target} keyword {keyword}")
    return data

def _as_noun(keyword: str) -> str:
    """Turn whatever was typed into a phrase that can sit inside a sentence."""
    text = re.sub(r"\s+", " ", keyword or "this service").strip(" ?.")
    text = re.sub(r"^(who|what|which|how|where|why)\s+(is|are|does|do|should|can|will)\s+", "", text, flags=re.I)
    text = re.sub(r"^(the\s+)?best\s+", "", text, flags=re.I)
    text = re.sub(r"\bnear me\b", "near you", text, flags=re.I)
    acronyms = {"seo", "ai", "ios", "api", "faq", "html", "usa", "uk"}
    small = {"a", "an", "the", "in", "of", "for", "and", "or", "to", "on", "with", "near", "by", "at"}
    words = []
    for word in text.split():
        low = word.lower()
        words.append(low.upper() if low in acronyms else low)
    if " in " in " ".join(words):
        head, place = " ".join(words).rsplit(" in ", 1)
        place = " ".join(part[:1].upper() + part[1:] for part in place.split())
        phrase = f"{head} in {place}"
    else:
        phrase = " ".join(words)
    for word in small:
        phrase = re.sub(rf"\b{word}\b", word, phrase)
    if re.match(r"^(a|an|the)\b", phrase, flags=re.I):
        return phrase[:1].lower() + phrase[1:]
    countable = re.search(
        r"\b(company|companies|agency|agencies|firm|firms|designer|designers|developer|developers|videographer|videographers|photographer|photographers|consultant|consultants|studio|studios|service|services|provider|providers|expert|experts|specialist|specialists)\b",
        phrase,
        flags=re.I,
    )
    if not countable:
        return phrase
    article = "an" if re.match(r"^(seo|faq|html|api|[aeiou])", phrase, flags=re.I) else "a"
    return f"{article} {phrase}"


def _sentence_noun(keyword: str) -> str:
    phrase = _as_noun(keyword)
    return phrase[:1].upper() + phrase[1:]


def _place_name(keyword: str) -> str:
    match = re.search(r"\bin\s+([^,]+)", keyword or "", flags=re.I)
    if not match:
        return ""
    city = match.group(1).strip(" .")
    if not city or city.lower() in {"the", "a", "an"}:
        return ""
    return " ".join(part[:1].upper() + part[1:] for part in city.split())


_LENGTH_TEMPLATE = (
    "the first decision",
    "what must work in",
    "what a later edit looks like",
    "the useful page names the job",
    "people looking for",
    "what should the brief include",
    "home page has to say",
    "separate page for each",
    "asks for the work",
)


def _is_length_template(html: str) -> bool:
    text = re.sub(r"<[^>]+>", " ", html or "").lower()
    return sum(mark in text for mark in _LENGTH_TEMPLATE) >= 2


def _work_label(kind: str) -> str:
    return {
        "video": "recording",
        "app": "app",
        "web": "site",
        "seo": "search plan",
        "store": "store",
        "wordpress": "site",
        "cost": "quote",
    }.get(kind, "project")


def _service_name(keyword: str) -> str:
    topic = re.sub(r"\s+", " ", keyword or "this service").strip(" ?.")
    city = _place_name(topic)
    shown = _as_noun(topic)
    if city:
        shown = re.sub(rf"\s+in\s+{re.escape(city)}\b.*$", "", shown, flags=re.I).strip(" ,.")
    return shown or topic


def _body(*paragraphs: str) -> str:
    return "\n\n".join(part.strip() for part in paragraphs if part and part.strip())


def _an(word: str) -> str:
    return "an" if (word or "a")[:1].lower() in "aeiou" else "a"


def _eight(*sentences: str) -> str:
    clean = [part.strip().rstrip(".") + "." for part in sentences if part and part.strip()]
    return _body(*_short_lines(" ".join(clean)))


def _safe_sections(keyword: str) -> list[dict]:
    """Same shape as a finished local article: three specific sections, 8 or 9 sentences each."""
    topic = re.sub(r"\s+", " ", keyword or "this service").strip(" ?.")
    kind = _work_kind(topic.lower())
    if re.search(r"wordpress", topic, flags=re.I):
        kind = "wordpress"
    city = _place_name(topic) or "your area"
    shown = _service_name(topic)
    if kind in {"web", "wordpress"}:
        built = "WordPress" if kind == "wordpress" else "a custom site"
        return [
            {
                "title": "Local Design Strategy",
                "body": _eight(
                    f"A {shown} page for {city} should open with the services, the service area, and a way to get in touch",
                    f"Local businesses need the work named in plain language, with photos of finished jobs from the same kind of project",
                    f"The layout should stay clear on a phone, because many people in {city} will look at it away from a desk",
                    f"Navigation should lead to the services, the project examples, and the contact details without a long hunt",
                    f"Building on {built} is a practical choice when the owner needs to update service text and photos later",
                    f"The design should still look like the business, not like a template with the city name swapped in",
                    f"A short line under the headline can name the neighborhoods around {city} that the business actually covers",
                    f"The page is doing its job when a resident can tell what is offered and whether the company works nearby",
                    "A design that fits the city is one a customer can explain back in a single sentence",
                ),
            },
            {
                "title": "SEO and Visibility",
                "body": _eight(
                    f"The title and the first paragraph should both say the service and {city}, because that is the search the page is for",
                    "One page should answer one search, with the service page and the city page linked to each other",
                    "On-page details that help are the business name, the address, the service area, and a phone number people can tap",
                    f"Project pages and short answers about common jobs give {city} readers a reason to stay and a crawler more relevant text",
                    "A mobile layout matters here, because a page that is hard to read on a phone is easy to leave",
                    "Use the same service name in the menu, the heading, and the opening so the offer does not change from one line to the next",
                    "Skip extra city names the business does not serve, since those pages create calls you cannot take",
                    f"The useful result is a {city} page that matches the search and still gives the reader a way to ask for the work",
                    "Keep the same facts in the title, the heading, and the contact block",
                ),
            },
            {
                "title": "Conversion Optimization",
                "body": _eight(
                    f"A {shown} visit in {city} should end in a call, a form, or a request for a quote",
                    "Put that action on the home page and again after the services, with the phone number written out so it can be tapped",
                    "The form only needs a name, a number, the service, and a short note about the job",
                    "Trust details belong beside it: a few real project photos, the service area, and a sentence about how a reply is made",
                    "A live chat or a second form is optional, and only if someone will actually answer it",
                    "The confirmation should say the message arrived and repeat the phone number",
                    f"Do not send the reader to an unrelated page after they ask for work in {city}",
                    "Clear contact, visible proof, and one next step are what turn the visit into an inquiry",
                    "That is enough for a contractor site to be useful without extra sections",
                ),
            },
        ]
    if kind == "app":
        return [
            {
                "title": "Local Product Fit",
                "body": _eight(
                    f"An app for {city} is useful when a person can finish one job on it, such as booking, ordering, or checking a request",
                    "Name that job on the first screen, and name who it is for",
                    f"A customer in {city} does not need the same buttons as a manager, so the first version should serve the person who starts the job",
                    "Ask for an address, an account, or a payment only when that step needs it",
                    "Keep the labels in ordinary language, the same words a person would use for the task",
                    "Show the confirmation before they leave, with the request repeated back to them",
                    "If something is missing, keep what they already entered and say what to fix",
                    f"The first release is ready when someone in {city} can finish that job without help",
                ),
            },
            {
                "title": "Performance on a Phone",
                "body": _eight(
                    "Build the path on a phone before a large screen, with type that can be read and buttons that can be tapped",
                    f"People in {city} will use it on ordinary connections, so the main job should still finish when the network is slow",
                    "A screen that only works on a fast office connection is not ready",
                    "Errors should be specific, and the app should let the person try again",
                    "Do not add reports, extra accounts, or settings until the main job is reliable",
                    "Test the path once as a new user and note every place they hesitate",
                    "Those notes are the revision list",
                    "A comment that only says to make it better does not tell anyone what to change",
                ),
            },
            {
                "title": "From a Visit to a Start",
                "body": _eight(
                    f"The page or store listing for the app should say the job, the {city} area, and how to begin",
                    "Screenshots should show that job, not a generic phone frame",
                    "The first step after install should be the task itself, not a long tour",
                    "If an account is required, explain why in one sentence",
                    "A support path, such as a phone number or a short form, belongs where the person gets stuck",
                    "Measure success by completed jobs, not by how many screens were built",
                    f"Add another feature only after people in {city} can finish the first one",
                    "That keeps the app understandable for the person who downloaded it",
                ),
            },
        ]
    if kind == "seo":
        return [
            {
                "title": "Pages That Match the Search",
                "body": _eight(
                    f"A search for this service in {city} should open a page that names the service and the city in the title and the first paragraph",
                    "One page should own one search",
                    "The service page explains the offer, and a city page is worth publishing only when the business actually works there",
                    "The opening should say what the customer gets and how to ask for it",
                    "Use the same service name in the title, the heading, and the menu",
                    "Photos need captions that say what the work was",
                    "Do not publish a list of cities you cannot support",
                    f"A reader in {city} should recognize the offer before they reach the end of the first screen",
                ),
            },
            {
                "title": "Local Visibility",
                "body": _eight(
                    f"Link the {city} page and the main service page to each other",
                    "Include the business name, the area served, and a phone number on the page",
                    "Answer the questions a buyer asks before calling, such as what is included and how a project starts",
                    "Keep those answers on the service page instead of scattering them across unrelated posts",
                    "A page that is hard to read on a phone will not hold the visit",
                    "After publishing, read the title and the first paragraph again to be sure they still agree",
                    "If a new service is added, give it a page of its own",
                    "Copying one city page and swapping the name is not a local page",
                ),
            },
            {
                "title": "Visits That Become Calls",
                "body": _eight(
                    "The page should end with a phone number and a short form",
                    "Ask for a name, a number, and the service",
                    f"Say that the work is available in {city} next to that form",
                    "The confirmation should repeat the number for someone who would rather call",
                    "Proof, such as a project photo and the area served, belongs near the contact details",
                    "Do not hide the next step in the footer only",
                    "A page that is found and then offers no way to start has not finished",
                    "The useful set is the service page, an honest city page, and a clear way to get in touch",
                ),
            },
        ]
    if kind == "store":
        return [
            {
                "title": "What the Shopper Sees",
                "body": _eight(
                    f"A store serving {city} has to show the product, the price, and a way to pay on the same visit",
                    "The first screen should open the catalog, not a long brand story",
                    "Each product page needs the name, the photo, what is included, and the price",
                    "Size or color choices belong on that page",
                    f"Say whether you ship to {city}, deliver there, or offer pickup before the buyer pays",
                    "Returns and a way to reach the shop should be easy to find",
                    "A buyer who learns a limit only after payment has a reason to cancel",
                    "The product page is doing its job when the item and the cost are obvious",
                ),
            },
            {
                "title": "Catalog and Checkout",
                "body": _eight(
                    "Group products by the type of item a buyer would search for",
                    "The category page should show the item, the price, and a photo",
                    "The cart should show the quantity and the total, and let the buyer change the quantity there",
                    "Checkout then asks for the address, the delivery choice, and the payment",
                    "Show which step they are on",
                    "Do not require an account unless the order cannot be completed without one",
                    f"If you do not deliver to an address near {city}, say so before payment",
                    "A test order on a phone should match the receipt",
                ),
            },
            {
                "title": "After the Order",
                "body": _eight(
                    "The confirmation should repeat the item, the total, and where it is going",
                    "The receipt should say the same thing",
                    f"Explain how a {city} delivery, shipment, or pickup works in one short paragraph",
                    "If pickup is offered, give the address and how the buyer knows the order is ready",
                    "Say what can be returned and how to start",
                    "A hidden return policy costs the next order from the same person",
                    "Banners can wait until a shopper can find an item and finish paying",
                    "The catalog, the product page, and the checkout are the store",
                ),
            },
        ]
    if kind == "video":
        return [
            {
                "title": "The Event Being Recorded",
                "body": _eight(
                    f"A {shown} page for {city} should say which events you record and which you do not",
                    "A wedding, a talk, and a property tour need different shot lists",
                    f"Name {city} as the place you work, and mention travel only if you really offer it",
                    "Show finished examples of the same kind of event, labeled with the job",
                    "Say what the client receives, such as the edited film, the speeches, or a short cut",
                    "That deliverable belongs near the top, because it is what people compare",
                    "A camera list is less useful than a clear description of the film",
                    "The reader should know the event, the city, and the film before they reach the form",
                ),
            },
            {
                "title": "What to Agree Beforehand",
                "body": _eight(
                    f"Write down the place in {city}, the parts of the event you will cover, and who approves the edit",
                    "Ask for the schedule and the moments that must be captured",
                    "The page can say that this list is needed before the date",
                    "One review against that list is easier to understand than an open request to change anything",
                    "A missing moment counts only when it was on the list and it is not in the film",
                    "Put a phone number next to the booking form for the day of the event",
                    "The examples on the page should be the same kind of event you are offering",
                    "If they are not, replace them before the page is public",
                ),
            },
            {
                "title": "How a Booking Starts",
                "body": _eight(
                    "The form should ask for the date, the place, the type of event, and a phone number",
                    "That is enough for a reply",
                    f"The reply should confirm that you work in {city} and restate the film they asked about",
                    "If the date is not open, say so",
                    "After the event, deliver the film you named on the page",
                    "A link with no note about what it contains creates another round of questions",
                    "The page, the examples, and the form should describe the same service",
                    "A visitor should be able to tell what you record, what they receive, and how to reserve the date",
                ),
            },
        ]
    return [
        {
            "title": f"The Work in {city}",
            "body": _eight(
                f"{shown[:1].upper() + shown[1:]} in {city} should say what is offered and who it is for in the opening",
                "List the parts of the work you actually do, and say if one part is the main job",
                "A reader can then tell whether their request fits",
                f"Name {city} as the area you cover, and add other places only when you serve them",
                "An example should be the same kind of job, with what the client received",
                "A logo is not an example",
                "If the example is from somewhere else, say so",
                "The opening, the list, and the example should agree",
            ),
        },
        {
            "title": "What a Client Can Check",
            "body": _eight(
                "Say what you need before the work starts, such as access, documents, or a decision from the client",
                "Naming those items on the page saves a call that only collects the same facts",
                "A second example helps only when it is a different job of the same service",
                "Say who replies after an inquiry",
                "One path is easier to trust than a promise that someone will be in touch",
                "Do not invent a price or a timeline on the page",
                f"Ask for the address in {city} only when the job needs a visit",
                "The reader should finish this section knowing what the work includes and what they must provide",
            ),
        },
        {
            "title": "How an Inquiry Starts",
            "body": _eight(
                "Offer one phone number and a short form",
                "The form needs a name, a number, the service, and a sentence about the job",
                "The confirmation should say the message arrived and repeat the number",
                f"In the reply, restate the service and {city}",
                "If you cannot take the request, say so",
                "If several people handle inquiries, still publish the number that is actually answered",
                "A second number that nobody checks creates a missed job",
                "The page is complete when the service, the area, one example, and the next step are all visible",
            ),
        },
    ]


_SHORT_BACKUP = (
    "scope is visible on the first read",
    "before extra ideas are added",
    "still needs a fix",
    "a plan that only lists hopes",
    "the review is a list, not a feeling",
)


def _is_short_backup(html: str) -> bool:
    text = re.sub(r"<[^>]+>", " ", html or "").lower()
    return sum(mark in text for mark in _SHORT_BACKUP) >= 2


def _safe_keyword_draft(keyword: str) -> dict:
    topic = re.sub(r"\s+", " ", keyword or "this service").strip(" ?.")
    shown = _service_name(topic)
    city = _place_name(topic) or "your area"
    lines, _scene, _tail = _topic_lines(topic.lower())
    offer = re.sub(r"^(a|an)\s+", "", shown, flags=re.I)
    meta = (
        f"Discover expert {offer} in {city}, tailored to local businesses seeking a professional online presence."
    )
    return {
        "_from_model": True,
        "_canned": True,
        "tagline": lines[0],
        "meta_description": meta,
        "introduction": (
            f"A clear {shown} presence in {city} helps local customers see the services, the area covered, and an easy way to make contact. "
            f"The page should reflect the business and stay easy to use on a phone.\n\n"
            f"The work that follows is specific to {city}: how the offer is presented, how the page can be found, and how a visit becomes an inquiry."
        ),
        "steps": _safe_sections(keyword),
        "faqs": [
            {"question": f"What makes {shown} in {city} useful to a local customer?", "answer": f"It names the services, shows relevant work, states the {city} area, and gives a phone number or form that is easy to find."},
            {"question": f"How can this page be found by people in {city}?", "answer": f"Use the service and {city} in the title and the opening, keep the page readable on a phone, and link it from the main service page."},
            {"question": "What turns a visit into an inquiry?", "answer": "A visible phone number, a short form, proof of the work, and a confirmation that the message was received."},
        ],
    }

def _parse_accurate(data: dict | None, keyword: str) -> dict | None:
    if not isinstance(data, dict) or data.get("__rate_limited"):
        return None
    steps = []
    for step in (data.get("sections") or data.get("steps") or []):
        if not isinstance(step, dict):
            continue
        title = str(step.get("title") or "").strip()
        body = str(step.get("body") or "").strip()
        if title and body and not re.search(r"^(what to prepare|how the page is structured|what the visitor should see|after the first version)\b", title, flags=re.I):
            shown = _pretty_keyword(keyword)
            title = re.sub(rf"^{re.escape(shown)}\s*[:|\-–]\s*", "", title, flags=re.I).strip()
            title = re.sub(rf"^{re.escape(keyword)}\s*[:|\-–]\s*", "", title, flags=re.I).strip()
            if title.lower().startswith(keyword.lower()):
                title = title[len(keyword):].lstrip(" :|-–").strip()
            if title:
                steps.append({"title": title, "body": body})
        if len(steps) == 3:
            break
    faqs = [item for item in (data.get("faqs") or []) if isinstance(item, dict)][:3]
    if len(steps) < 3:
        return None
    foreign = ("swift", "swiftui", "kotlin", "react native", "wordpress", "shopify", "videography", "keynote")
    blob = keyword.lower()

    def _off_topic(text: str) -> bool:
        return any(name not in blob and re.search(rf"\b{re.escape(name)}\b", text or "", flags=re.I) for name in foreign)

    tagline = str(data.get("tagline") or "").strip()
    if _off_topic(tagline):
        tagline = ""
    steps = [step for step in steps if not _off_topic(step["title"] + " " + step["body"])]
    faqs = [item for item in faqs if not _off_topic(json.dumps(item))]
    if len(steps) < 3:
        return None
    canned = [str(step.get("title") or "").strip().lower() for step in steps]
    if canned == ["architecture", "build process", "platforms"]:
        return None
    return {
        "_from_model": True,
        "tagline": tagline,
        "introduction": str(data.get("introduction") or "").strip(),
        "steps": steps,
        "faqs": faqs,
        "meta_description": str(data.get("meta_description") or "").strip(),
        "search_intent": str(data.get("search_intent") or "").strip().lower(),
        "detected_industry": str(data.get("detected_industry") or "").strip(),
        "detected_audience": str(data.get("detected_audience") or "").strip(),
    }

async def _accurate_draft(keyword: str, keyword_length: str = "short", word_count: int = 800, repair: str = "") -> dict:
    """Write this keyword. A second writer is the backup. Neither path uses another service's copy."""
    length = "Use a short keyword phrase, about 2 to 4 words." if keyword_length != "long" else "Use a longer keyword phrase, about 6 to 10 words, still about this service."
    each = "3 or 4 lines, then a new paragraph. Never one long block"
    fix = f" The last draft failed: {repair}. Correct only that problem." if repair else ""
    prompt = (
        f"The keyword is: {keyword}. {length}{fix} "
        "Decide the search intent first: informational, commercial, transactional, or local. "
        "Write only about this keyword. Support AI, generative AI, LLM, RAG, AEO, GEO, SEO, and AI search visibility when the keyword is about them. "
        "Do not insert those topics into an ordinary service article. "
        "Do not invent prices, rankings, statistics, or customer results. Do not give a duration. Do not say hours, days, weeks, months, or years. "
        "Use only the city named in the keyword. Do not add a second city. Do not name a technology or industry that the keyword does not contain. "
        "Mention ZeOrbit only once, and only if the keyword is a service ZeOrbit actually offers. "
        "Return JSON with these keys: "
        "search_intent, detected_industry, detected_audience, "
        "tagline (4 to 7 words that fit this service and do not repeat the keyword), "
        "meta_description (one readable sentence, 140 to 160 characters, no unsupported claims), "
        "introduction (two paragraphs about this keyword, separated by a blank line), "
        f"sections (exactly 3 objects with title and body; titles are specific, like Local Design Strategy, SEO and Visibility, and Conversion Optimization for a website; each body is {each}), "
        "faqs (exactly 3 objects with question and answer a person searching this keyword would ask). "
        "Write a local service article. The title is the service and the one city in the keyword. "
        "The introduction is two paragraphs that mention the service and that city inside normal sentences. "
        "Each section heading names the topic, such as a local strategy or a practical check, and does not paste the full keyword. "
        "Every sentence stays on this service and this city. "
        "Use the full keyword at most four times in the body, only inside a complete sentence. "
        "Never use these headings: What Should You Look For, Which Parts Matter Here, How to Choose Help, What to prepare, How the page is structured, What the visitor should see, After the first version, What the work covers, How the work is checked, How to compare options, The first decision, What must work on a phone, What a later edit looks like, What should the brief include. "
        "Each paragraph is 3 or 4 lines and then stops. Start a new paragraph after that. Do not write a wall of text. "
    )
    for _round in range(2):
        data = await _groq_json(prompt, max_tokens=1800, timeout=20)
        parsed = _parse_accurate(data, keyword)
        if parsed:
            return parsed
        data = await _groq_json(prompt, max_tokens=1800, model="openai/gpt-oss-20b", timeout=20)
        parsed = _parse_accurate(data, keyword)
        if parsed:
            return parsed
        try:
            from services.llm_service import chat_json
            data = await chat_json(prompt, temperature=0.3, max_tokens=1800, provider="gemini")
        except Exception as exc:
            print(f"[blog] backup writer error: {exc}")
            data = None
        parsed = _parse_accurate(data if isinstance(data, dict) else None, keyword)
        if parsed:
            return parsed
    print(f"[blog] using service template for {keyword}")
    return _safe_keyword_draft(keyword)

async def _generate(keyword: str, button_label: str = "", button_url: str = "", word_count: int = 800, strict: bool = True, keyword_length: str = "short") -> dict:
    layout = _reserve_layout()
    target = min(900, max(800, int(word_count or 850)))
    draft = await _accurate_draft(keyword, keyword_length, target)
    packed = _pack(draft, keyword, button_label, button_url, layout)
    structural = [
        item for item in _problems(packed.get("content_html") or "", keyword, target)
        if item != "article is too short"
    ]
    if structural and draft.get("_from_model") and "Scoped to This Service" not in str(draft.get("tagline") or ""):
        draft = await _accurate_draft(keyword, keyword_length, target, repair="; ".join(structural[:3]))
        if draft:
            packed = _pack(draft, keyword, button_label, button_url, layout)
    if not draft.get("_canned"):
        packed = await _expand_to_length(packed, keyword, target)
    packed["content_html"] = _split_html_paragraphs(_cap_keyword_html(
        _strip_invented_claims(packed.get("content_html") or "", keyword),
        keyword,
        6,
    ))
    packed["word_count"] = _article_words(packed.get("content_html") or "")
    if _is_length_template(packed.get("content_html") or ""):
        packed = _pack(_safe_keyword_draft(keyword), keyword, button_label, button_url, layout)
        packed["word_count"] = _article_words(packed.get("content_html") or "")
    if _is_short_backup(packed.get("content_html") or "") or _is_length_template(packed.get("content_html") or ""):
        raise RuntimeError("The writer is busy. Generate this post again.")
    left = _problems(packed.get("content_html") or "", keyword, target)
    if left:
        print(f"[blog] remaining checks for {keyword}: {left}")
    return packed

async def _save_draft(session: AsyncSession, packed: dict, owner_email: str = "") -> str:
    if _is_short_backup(packed.get("content_html") or "") or _is_length_template(packed.get("content_html") or ""):
        raise RuntimeError("The writer is busy. Generate this post again.")
    slug, existing, owner = await claim_slug(session, _slug(packed.get("slug") or ""), owner_email)
    payload = dict(packed)
    payload["slug"] = slug
    payload["content_type"] = "blog"
    payload["publish_status"] = "draft"
    payload["saved_at"] = datetime.now(timezone.utc).isoformat()
    industry = str(packed.get("detected_industry") or "Blog")
    if existing:
        existing.seo_block = payload
        existing.updated_at = datetime.now(timezone.utc)
        existing.business_type = industry or existing.business_type
        existing.owner_email = owner
    else:
        session.add(PageRecord(
            business_type=industry,
            base_location="",
            city=str(packed.get("city") or ""),
            state=str(packed.get("state") or ""),
            slug=slug,
            owner_email=owner,
            seo_block=payload,
        ))
    return slug

class BlogRepairRequest(BaseModel):
    slug: str = ""
    keyword: str = ""
    city: str = ""
    state: str = ""


def _repair_topic(keyword: str, city: str, state: str) -> str:
    topic = re.sub(r"\s+", " ", keyword or "").strip()
    city = re.sub(r"\s+", " ", city or "").strip()
    state = re.sub(r"\s+", " ", state or "").strip()
    if city and city.lower() not in topic.lower():
        topic = f"{topic} in {city}" + (f", {state}" if state else "")
    return topic


@router.post("/repair")
async def repair_nonsense(req: BlogRepairRequest, session: AsyncSession = Depends(get_session)):
    """Replace the old brief/phone/later-edit article with the service article."""
    topic = _repair_topic(req.keyword, req.city, req.state)
    if len(topic) < 2:
        raise HTTPException(status_code=422, detail="Enter a keyword.")
    packed = _pack(_safe_keyword_draft(topic), topic)
    packed["keyword"] = topic
    packed["city"] = req.city
    packed["state"] = req.state
    if req.slug:
        packed["slug"] = req.slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == req.slug))
        row = result.scalar_one_or_none()
        block = row.seo_block if row and isinstance(row.seo_block, dict) else None
        if block is not None and _is_length_template(block.get("content_html") or ""):
            from sqlalchemy.orm.attributes import flag_modified
            block = dict(block)
            block.update({
                "content_html": packed["content_html"],
                "title": packed.get("title") or block.get("title"),
                "seo_title": packed.get("seo_title") or block.get("seo_title"),
                "meta_description": packed.get("meta_description") or block.get("meta_description"),
                "keyword": topic,
            })
            row.seo_block = block
            flag_modified(row, "seo_block")
            await session.commit()
    return packed


@router.post("/generate")
async def generate_blog(req: BlogGenerateRequest):
    keyword = re.sub(r"\s+", " ", req.keyword).strip()
    if len(keyword) < 2:
        raise HTTPException(status_code=422, detail="Enter a keyword.")
    length = "long" if req.keyword_length.strip().lower() == "long" else "short"
    try:
        return await _generate(keyword, req.button_label.strip(), req.button_url.strip(), req.word_count, keyword_length=length)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.post("/generate-batch")
async def generate_blog_batch(
    req: BlogBatchRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_optional_user),
):
    from services.location_service import cities_in_county

    keyword = re.sub(r"\s+", " ", req.keyword).strip()
    picks = list(req.counties)
    if not picks and req.county and req.state:
        picks = [CountyPick(name=req.county, state=req.state)]
    if req.cities:
        from services.location_service import _STATE_CODE_TO_NAME
        places = []
        for item in req.cities:
            code = (item.state or "").strip().upper()
            state_name = item.state_name or ""
            if len(state_name) <= 2:
                state_name = _STATE_CODE_TO_NAME.get(code, state_name or code)
            places.append({
                "city": item.city,
                "state": code or state_name,
                "state_name": state_name,
                "county": item.county,
            })
        picks = picks or [CountyPick(name=places[0]["county"] or "County", state=places[0]["state_name"] or places[0]["state"] or "US")]
    elif not picks:
        raise HTTPException(status_code=422, detail="Select at least one US county.")
    else:
        places = []
    if not places:
        seen = set()
        per_county = max(1, req.count // len(picks))
        for pick in picks:
            for place in cities_in_county(pick.state, pick.name, per_county):
                key = (place["city"].lower(), place["state"])
                if key in seen:
                    continue
                seen.add(key)
                places.append(place)
                if len(places) >= req.count:
                    break
            if len(places) >= req.count:
                break
    if not places:
        raise HTTPException(status_code=422, detail="No cities were found for those counties.")
    sem = asyncio.Semaphore(2)
    created = []
    failed = []
    used_slugs: set[str] = set()

    def _topic_for(place: dict) -> str:
        base = re.sub(r"\s+", " ", keyword or "").strip().strip("?. ")
        base = re.sub(
            r"\b(?:in|near|around|across)\s+[A-Za-z][A-Za-z .'-]{1,60}$",
            "",
            base,
            flags=re.I,
        ).strip(" ,.-")
        return f"{base} in {place['city']}, {place['state_name']}"

    def _city_slug(city: str) -> str:
        city_part = _slug(city) or "city"
        stem = _slug(keyword)[:48].rstrip("-") or "post"
        slug = f"{city_part}-{stem}"[:80].rstrip("-")
        if slug not in used_slugs:
            return slug
        extra = 2
        while f"{slug[:70].rstrip('-')}-{extra}" in used_slugs:
            extra += 1
        return f"{slug[:70].rstrip('-')}-{extra}"

    async def write_place(place: dict) -> dict:
        topic = _topic_for(place)
        last_error = None
        for _attempt in range(2):
            try:
                async with sem:
                    return await _generate(topic, word_count=req.word_count, strict=False)
            except Exception as exc:
                last_error = exc
                print(f"[blog] batch writer failed for {place.get('city')}: {exc}")
        raise last_error

    for place in places:
        city = place["city"]
        try:
            packed = await write_place(place)
        except Exception as exc:
            failed.append({"city": city, "error": "The writer is busy. Generate this city again."})
            print(f"[blog] skipped short draft for {city}: {exc}")
            continue
        slug = _city_slug(city)
        used_slugs.add(slug)
        packed.update({
            "city": city,
            "state": place["state"],
            "county": place.get("county") or "",
            "state_name": place.get("state_name") or "",
            "slug": slug,
            "keyword": f"{keyword} in {city}, {place.get('state_name') or ''}".strip(),
            "primary_keyword": f"{keyword} in {city}",
            "publish_status": "draft",
        })
        saved = ""
        for attempt in range(2):
            try:
                async with session.begin_nested():
                    saved = await _save_draft(session, packed, getattr(user, "email", "") or "")
                await session.commit()
                break
            except Exception as exc:
                print(f"[blog] batch save failed for {city}: {exc}")
                await session.rollback()
                slug = _city_slug(f"{city}-{attempt + 2}")
                used_slugs.add(slug)
                packed["slug"] = slug
                saved = ""
        if not saved:
            failed.append({"city": city, "error": "This city could not be saved."})
            continue
        created.append({
            "city": city,
            "state": place.get("state_name") or place.get("state") or "",
            "county": place.get("county") or "",
            "slug": saved,
            "title": packed["title"],
            "seo_title": packed["seo_title"],
            "meta_description": packed["meta_description"],
            "content_html": packed.get("content_html") or "",
            "word_count": packed.get("word_count") or 0,
            "keyword": packed["keyword"],
            "primary_keyword": packed["primary_keyword"],
            "detected_industry": packed.get("detected_industry") or "",
            "detected_audience": packed.get("detected_audience") or "",
            "search_intent": packed.get("search_intent") or "",
            "related_keywords": packed.get("related_keywords") or [],
        })
    await session.commit()
    return {
        "keyword": keyword,
        "state": places[0]["state_name"],
        "county": places[0]["county"],
        "requested": len(places),
        "created": created,
        "failed": failed,
    }

class BlogDraftRequest(BaseModel):
    keyword: str = ""
    slug: str
    title: str = ""
    seo_title: str = ""
    meta_description: str = ""
    content_html: str
    detected_industry: str = ""
    city: str = ""
    state: str = ""

@router.post("/draft")
async def save_blog_draft(
    req: BlogDraftRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_optional_user),
):
    if _is_short_backup(req.content_html or "") or _is_length_template(req.content_html or ""):
        raise HTTPException(status_code=422, detail="The writer is busy. Generate this post again.")
    slug, existing, owner = await claim_slug(session, _slug(req.slug), getattr(user, "email", "") or "")
    block = dict(existing.seo_block or {}) if existing and isinstance(existing.seo_block, dict) else {}
    block.update({
        "keyword": req.keyword or block.get("keyword") or req.title,
        "slug": slug,
        "title": req.title or block.get("title") or req.seo_title,
        "seo_title": req.seo_title or block.get("seo_title") or "",
        "meta_description": req.meta_description or block.get("meta_description") or "",
        "content_html": req.content_html,
        "content": req.content_html,
        "detected_industry": req.detected_industry or block.get("detected_industry") or "",
        "city": req.city or block.get("city") or "",
        "state": req.state or block.get("state") or "",
        "content_type": "blog",
        "publish_status": block.get("publish_status") or "draft",
        "saved_at": datetime.now(timezone.utc).isoformat(),
    })
    industry = req.detected_industry or block.get("detected_industry") or "Blog"
    if existing:
        existing.seo_block = block
        existing.updated_at = datetime.now(timezone.utc)
        existing.business_type = industry or existing.business_type
        existing.owner_email = owner
        if req.city:
            existing.city = req.city
        if req.state:
            existing.state = req.state
    else:
        session.add(PageRecord(
            business_type=industry,
            base_location="",
            city=req.city,
            state=req.state,
            slug=slug,
            owner_email=owner,
            seo_block=block,
        ))
    await session.commit()
    return {"slug": slug, "saved": True}
