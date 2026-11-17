"""
Natural-language topic interpreter for "What should the content be about?"

Pipeline: Understand → Answer → Structure → SEO optimize → Localize.
User query always wins over industry / location / SEO templates.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

# Common typos → canonical forms (applied before intent detection)
_TYPO_MAP = (
    (r"\breastauarnt\b", "restaurant"),
    (r"\brestauraunt\b", "restaurant"),
    (r"\brestaurent\b", "restaurant"),
    (r"\brestraunt\b", "restaurant"),
    (r"\bdiffernce\b", "difference"),
    (r"\bdiference\b", "difference"),
    (r"\bseperate\b", "separate"),
    (r"\bcafes\b", "cafes"),
    (r"\bcafé\b", "cafe"),
    (r"\bmobilea\s*pp\b", "mobile app"),
    (r"\bwebsit\b", "website"),
    (r"\bseo\b", "SEO"),
)

_INSTRUCTION_RE = re.compile(
    r"(?:,?\s*)?(?:explain(?:\s+for)?|make it|write(?:\s+it)?|in simple(?:\s+language)?|"
    r"for\s+(?:new\s+)?(?:business\s+)?owners?|keep it|useful for|"
    r"in plain english|for beginners?)\b.*$",
    re.I,
)

_HOWTO_RE = re.compile(
    r"^\s*(?:how(?:\s+(?:can|do|to|does|should|would|might))?\b|"
    r"ways?\s+to\b|steps?\s+to\b|tips?\s+(?:to|for)\b)",
    re.I,
)
_WHAT_RE = re.compile(r"^\s*what\s+(?:is|are|does|do)\b", re.I)
_WHY_RE = re.compile(r"^\s*why\b", re.I)
_BEST_RE = re.compile(r"\b(?:best|top|must[- ]have|essential)\b", re.I)

_WEB_SERVICE_RE = re.compile(
    r"\b(?:website\s+design|web\s+design|wordpress|shopify|wix|squarespace|"
    r"website\s+maintenance|website\s+redesign|new\s+business\s+website|"
    r"seo\s+services?|ppc|landing\s+page)\b",
    re.I,
)


def _pick(seed: str, pool: list[str]) -> str:
    if not pool:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[idx]


def correct_topic_typos(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    for pat, repl in _TYPO_MAP:
        t = re.sub(pat, repl, t, flags=re.I)
    return t


def _strip_writing_instructions(text: str) -> tuple[str, str]:
    """Split topic from writing instructions like 'explain for new business owners'."""
    raw = (text or "").strip()
    m = _INSTRUCTION_RE.search(raw)
    if not m or m.start() < 8:
        # Also split on explicit comma instruction
        parts = re.split(r",\s*(?=explain|make it|write|for new|in simple)", raw, maxsplit=1, flags=re.I)
        if len(parts) == 2 and len(parts[0].strip()) >= 3:
            return parts[0].strip(" ,"), parts[1].strip()
        return raw, ""
    topic = raw[: m.start()].strip(" ,")
    instr = raw[m.start() :].strip(" ,")
    return (topic or raw), instr


def _looks_like_compare(text: str) -> bool:
    low = (text or "").lower()
    if re.search(r"\b(?:vs\.?|versus|difference(?:s)?\s+between|compare(?:d)?\s+(?:to|with))\b", low):
        return True
    if re.search(r"\b([a-z][a-z0-9'-]{2,28})\s+and\s+([a-z][a-z0-9'-]{2,28})\s+difference\b", low):
        return True
    if re.search(r"\b(restaurant|reastauarnt|resto).{0,40}(cafe|café)", low) and re.search(
        r"\b(difference|differ|vs|hybrid|or)\b", low
    ):
        return True
    if re.search(r"\b(restaurant|reastauarnt)\s*/\s*(cafe|café)\b", low):
        return True
    return False


def interpret_topic(raw: str, keywords: list | None = None) -> dict[str, Any]:
    """Understand what the user is asking before any SEO template runs."""
    blob = " ".join(
        [str(raw or "").strip()]
        + [str(k).strip() for k in (keywords or []) if str(k).strip()]
    ).strip()
    # Prefer the longest / first user chip as primary
    if keywords:
        primary = str(keywords[0] or "").strip() or blob
    else:
        primary = blob
    cleaned = correct_topic_typos(primary)
    topic_core, instruction = _strip_writing_instructions(cleaned)
    topic_core = correct_topic_typos(topic_core)
    low = topic_core.lower().strip()

    audience = ""
    style = "practical"
    if instruction:
        if re.search(r"simple|plain|beginner|easy", instruction, re.I):
            style = "simple"
        if re.search(r"owner|business", instruction, re.I):
            audience = "business owners"
        if re.search(r"new business", instruction, re.I):
            audience = "new business owners"

    wants_app = bool(re.search(r"\b(mobile\s*app|ios|android|\bapp\b)\b", low))
    intent = "explain"
    entities: list[str] = []

    if _looks_like_compare(topic_core) or _looks_like_compare(cleaned):
        intent = "compare"
        # Prefer known foodservice pair
        if re.search(r"restaurant|reastauarnt|resto", low) and re.search(r"cafe|café", low):
            entities = ["Restaurant", "Cafe"]
        else:
            m = re.search(
                r"(?:difference(?:s)?\s+between)\s+(.+?)\s+and\s+(.+?)(?:\?|$)",
                low,
            ) or re.search(r"^(.+?)\s+(?:vs\.?|versus)\s+(.+?)$", low)
            if m:
                entities = [m.group(1).strip().title()[:40], m.group(2).strip().title()[:40]]
    elif _HOWTO_RE.search(low) or re.search(r"\bget more customers|attract more|increase (?:sales|traffic|bookings)\b", low):
        intent = "howto"
    elif _WHY_RE.search(low):
        intent = "why"
    elif _WHAT_RE.search(low) or re.search(r"^\s*what\s+is\b", low):
        intent = "what"
    elif _BEST_RE.search(low) and (
        re.search(r"\b(feature|features|tip|tips|idea|ideas|way|ways|tool|tools)\b", low)
        or wants_app
        or re.search(r"\bbest\b", low)
    ):
        intent = "best"
    elif _WEB_SERVICE_RE.search(low) or re.search(
        r"\b(build|redesign|maintain).{0,20}(website|site|shopify|wordpress)\b", low
    ):
        intent = "service_pitch"
    elif len(low.split()) <= 3 and not re.search(r"[?]", topic_core):
        # Single word / short phrase → broad informational topic
        intent = "broad"
        entities = [topic_core]

    # Entity hints for foodservice
    if re.search(r"\brestaurants?\b", low):
        if "Restaurant" not in entities:
            entities.append("Restaurant")
    if re.search(r"\bcafes?\b|\bcafé\b", low):
        if "Cafe" not in entities:
            entities.append("Cafe")

    focus = topic_core
    secondary = []
    if intent == "compare" and wants_app:
        secondary.append("mobile_app")

    return {
        "raw": primary,
        "cleaned": cleaned,
        "topic": focus,
        "intent": intent,
        "entities": entities,
        "instruction": instruction,
        "audience": audience,
        "style": style,
        "wants_app": wants_app,
        "secondary": secondary,
        "use_topic_article": intent != "service_pitch",
    }


def _place_bit(city: str) -> str:
    place = re.split(r"\s*,\s*", (city or "").strip(), maxsplit=1)[0].strip()
    place = re.sub(r"\b\d{5}(?:-\d{4})?\b", "", place).strip(" -.,")
    return f" in {place}" if place else ""


def _faq(items: list[tuple[str, str]]) -> list[dict]:
    return [{"question": q, "answer": a} for q, a in items]


def _soft_cta(topic: str, city: str = "") -> str:
    place = _place_bit(city)
    return (
        f"Need a clear website or mobile app for {topic.lower()}{place}? "
        f"ZeOrbit can help — call 619-724-9517 or visit www.zeorbit.com."
    )


def _singular(trade: str) -> str:
    t = (trade or "").strip()
    if t.endswith("inesses"):
        return t[:-2]
    if t.endswith("ies"):
        return t[:-3] + "y"
    if t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t


def _readable_phrase(text: str) -> str:
    """Split glued words such as realestate and keep product names readable."""
    t = re.sub(r"\s+", " ", (text or "").strip())
    swaps = (
        (r"real[\s-]*estate", "real estate"),
        (r"wordpress", "WordPress"),
        (r"ios", "iOS"),
        (r"iphone", "iPhone"),
        (r"android", "Android"),
    )
    for pattern, repl in swaps:
        t = re.sub(pattern, repl, t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()


def _fit_words(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut or text[:limit].rstrip()


def _audience_and_offer(subject: str) -> tuple[str, str]:
    """Pull who the query mentions, and a grammatical service name, for any topic."""
    t = _clean_subject(subject)
    audience = ""
    who_m = re.search(
        r"\b(small\s+business\s+owners?|business\s+owners?|homeowners?|patients?|customers?|agents?|brokers?)\b",
        t,
        flags=re.I,
    )
    if who_m:
        audience = who_m.group(1).lower()
        if not audience.endswith("s"):
            audience += "s"
        t = f"{t[: who_m.start()]} {t[who_m.end() :]}"
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(?:we|i|our(?:\s+team)?)\s+", "", t, flags=re.I)
    for pattern, repl in (
        (r"\bwix\b", "Wix"),
        (r"\bshopify\b", "Shopify"),
        (r"\bsquarespace\b", "Squarespace"),
        (r"\bwebflow\b", "Webflow"),
    ):
        t = re.sub(pattern, repl, t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ?.")
    verb = re.match(
        r"(fix|build|design|repair|maintain|create|launch|start|redesign|install)(?:ing|s|es)?\s+(?:the\s+|a\s+|an\s+|our\s+)?(.+)$",
        t,
        flags=re.I,
    )
    noun = {
        "fix": "fix", "repair": "repair", "maintain": "maintenance", "install": "installation",
        "build": "build", "design": "design", "create": "build", "launch": "launch",
        "start": "launch", "redesign": "redesign",
    }
    if verb:
        rest = re.sub(r"\b(store|site|website|page|app)s\b", r"\1", verb.group(2).strip(), flags=re.I)
        offer = f"a {rest} {noun[verb.group(1).lower()]}"
    else:
        offer = t or "a website update"
    return audience, offer


def _plain_offer(subject: str) -> str:
    return _audience_and_offer(subject)[1]


def _clean_subject(text: str) -> str:
    t = _readable_phrase(text)
    t = re.sub(
        r"^(?:please\s+|can you\s+|could you\s+|i need\s+|i want\s+|tell me\s+|explain\s+|write about\s+)",
        "",
        t,
        flags=re.I,
    )
    t = t.strip(" ?.!\"'`")
    t = re.sub(r"\b(?:plz|pls)\b", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ?.!")
    return t


def _subject_for_intent(topic: str, intent: str) -> str:
    t = _clean_subject(topic)
    if intent == "what":
        t = re.sub(r"^what\s+(?:is|are|does|do)\s+(?:a\s+|an\s+|the\s+)?", "", t, flags=re.I)
    elif intent == "howto":
        t = re.sub(
            r"^(?:how(?:\s+(?:can|do|to|does|should))?\s+|ways?\s+to\s+|steps?\s+to\s+|tips?\s+(?:to|for)\s+)",
            "",
            t,
            flags=re.I,
        )
    elif intent == "why":
        t = re.sub(r"^why\s+(?:is|are|do|does|should|would)?\s*", "", t, flags=re.I)
    elif intent == "best":
        t = re.sub(r"^(?:what\s+are\s+)?(?:the\s+)?(?:best|top|essential|must[- ]have)\s+", "", t, flags=re.I)
    t = _clean_subject(t) or _clean_subject(topic) or "this topic"
    return t


def _industry_fit_lists(industry: str, service: str = "") -> tuple[str, str]:
    """Build a long specialty list from the industry that was typed.

    Shown in the editor preview and hidden on the live page.
    """
    name = re.sub(r"\s+", " ", (industry or "local business").strip()) or "local business"
    low = name.lower()
    generic = low in {"local business", "local businesses", "business", "businesses", "company", "companies", "local"}
    if generic:
        concrete = [
            "contractors", "home service companies", "medical and dental practices",
            "law firms", "real estate teams", "restaurants and cafes",
            "auto shops", "retail stores", "professional services firms",
            "fitness studios", "salons", "multi-location local brands",
        ]
        mid = len(concrete) // 2
        def _join(items: list[str]) -> str:
            return ", ".join(items[:-1]) + ", and " + items[-1]
        return _join(concrete[:mid]), _join(concrete[mid:])
    work = re.sub(r"\s+", " ", (service or "website and mobile app").strip()).lower()
    extra: list[str] = []
    packs = (
        (("biopharma", "biotech", "pharma", "life science"), [
            "laboratory service providers", "genomics companies", "genetic testing providers",
            "molecular diagnostics companies", "precision medicine providers", "microbiology laboratories",
            "medical diagnostics companies", "medical device manufacturers", "clinical research organizations",
            "contract research organizations (CROs)", "contract development and manufacturing organizations (CDMOs)",
            "drug discovery companies",
        ]),
        (("health", "medical", "clinic", "dental", "hospital"), [
            "clinics", "specialty practices", "diagnostic labs", "outpatient centers",
            "medical groups", "urgent care providers", "dental practices", "home-health providers",
        ]),
        (("carpet", "floor", "contractor", "construct", "remodel"), [
            "residential installers", "commercial contractors", "remodeling crews",
            "property managers", "builders", "trade suppliers",
        ]),
        (("real estate", "realtor", "property"), [
            "residential real estate agents", "luxury real estate agents", "commercial real estate brokers",
            "property management companies", "real estate developers", "apartment leasing teams",
            "vacation rental managers", "title companies", "mortgage brokers", "home staging firms",
            "real estate photography teams", "HOA management companies",
        ]),
        (("restaurant", "cafe", "food", "hospitality"), [
            "independent restaurants", "cafe groups", "catering companies",
            "hotel restaurants", "food trucks", "multi-unit restaurant brands",
        ]),
    )
    for keys, rows in packs:
        if any(k in low for k in keys):
            extra.extend(rows)
    roles = [
        f"{low} companies",
        f"{low} startups",
        f"regional {low} firms",
        f"multi-location {low} operators",
        f"independent {low} providers",
        f"{low} suppliers",
        f"{low} consultants",
        f"franchise {low} brands",
        f"specialty {low} teams",
        f"B2B {low} vendors",
        f"{low} service networks",
        f"{'independent local businesses' if low == 'local' else f'local {low} businesses'} that need {work}",
    ]
    seen = set()
    ordered = []
    for item in extra + roles:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    mid = max(6, len(ordered) // 2)
    def _join(items: list[str]) -> str:
        if len(items) == 1:
            return items[0]
        return ", ".join(items[:-1]) + ", and " + items[-1]
    return _join(ordered[:mid]), _join(ordered[mid:])


def _reader_article(interp: dict, city: str = "", industry: str = "") -> dict:
    """One readable article for a word, a phrase, a question, or a messy sentence."""
    intent = interp.get("intent") or "explain"
    raw_topic = (interp.get("topic") or interp.get("cleaned") or "this topic").strip()
    subject = _subject_for_intent(raw_topic, intent)
    label = subject[:1].upper() + subject[1:]
    who = (industry or "").strip()
    who_l = who.lower()
    place = _place_bit(city)
    generic_who = who_l in {"", "local business", "local businesses", "business", "businesses"}
    field = "" if generic_who else (f" for {who_l}" if who else "")
    field_title = "" if generic_who else (f" for {who}" if who else "")
    where = "" if re.search(r"\bin\b", subject, re.I) else (place or "")

    if intent == "what":
        title = f"What {label} Means{field_title}{where}"
        lead = f"{label}{field} is easier to judge once you can say what it includes and what it leaves out{where}."
    elif intent == "howto":
        title = f"How to {label[:1].lower() + label[1:]}{field_title}{where}"
        lead = f"Here is a practical way to {subject}{field}{where}, from the first decision to a result you can use."
    elif intent == "why":
        title = f"Why {label}{field_title}{where}" if re.search(r"\b(matter|matters|important|worth)\b", subject, re.I) else f"Why {label} Matters{field_title}{where}"
        lead = f"{label} is worth explaining{field} because it changes a decision{where}."
    elif intent == "best":
        title = f"What to Look For in {label}{field_title}{where}"
        lead = f"The useful version of {subject}{field} is the one a customer can understand and act on{where}."
    elif intent in {"service_pitch", "broad"} or len(subject.split()) <= 6:
        title = f"{label}{field_title}{where}"
        lead = (
            f"{label}{field} means the work matches that field{where}, "
            f"instead of a generic page that could belong to any business."
            if who else
            f"{label}{where} is worth a clear explanation: what it is, who it helps, and how to start."
        )
    else:
        short = " ".join(subject.split()[:8])
        title = f"{short[:1].upper() + short[1:]}{field_title}{where}"
        lead = f"This article answers “{subject.rstrip('?')}”{field}{where} in plain language."

    if len(title) > 88:
        title = " ".join(title.split()[:12])

    title = _fit_words(title, 60)
    place_name = re.split(r"\s*,\s*", (city or "").strip(), maxsplit=1)[0].strip()
    low_subject = subject[:1].lower() + subject[1:]
    close_h = "If you want this built"
    close = (
        f"## {close_h}\n\n"
        f"ZeOrbit can build the website, or the iOS and Android app, around {low_subject}"
        f"{(' for ' + place_name) if place_name else ''}. "
        f"Call (619) 724-9517 or visit www.zeorbit.com.\n\n"
    )
    if intent == "howto":
        h2s = ["Where to start", f"Steps to {low_subject}", "Mistakes to avoid", close_h]
        body = (
            f"## {h2s[0]}\n\n"
            f"Start by writing the outcome in one sentence: what “{low_subject}” should change"
            f"{(' in ' + place_name) if place_name else ''}. "
            f"Name who it is for{field or ''}, what they already have, and the one result that counts as done.\n\n"
            f"## {h2s[1]}\n\n"
            f"1. Define {low_subject} in the words a customer would use.\n"
            f"2. List the pieces that have to exist before it is useful.\n"
            f"3. Put the most important piece first, then the proof, then the way to take the next step.\n"
            f"4. Read it once as the customer. Cut any line that does not help {low_subject}.\n\n"
            f"## {h2s[2]}\n\n"
            f"- Turning {low_subject} into a slogan instead of an answer\n"
            f"- Adding a city or an industry line that never mentions {low_subject}\n"
            f"- Skipping the step a person would actually take next\n\n"
            f"{close}"
        )
    elif intent == "what":
        h2s = [f"What {low_subject} means", f"What {low_subject} includes", "What it is not", close_h]
        body = (
            f"## {h2s[0]}\n\n"
            f"{label} is {low_subject} explained in plain language{where}. "
            f"A useful page says what it is, who it is for{field or ''}, and what someone can do with it.\n\n"
            f"## {h2s[1]}\n\n"
            f"- A direct definition of {low_subject}\n"
            f"- The parts that belong with it, named one by one\n"
            f"- A short example of {low_subject} in use{(' in ' + place_name) if place_name else ''}\n"
            f"- The next step after someone understands it\n\n"
            f"## {h2s[2]}\n\n"
            f"{label} is not a filler phrase for a different service. "
            f"If a sentence could be pasted onto any other topic, it does not belong in this article.\n\n"
            f"{close}"
        )
    elif intent == "why":
        why_h = f"Why {low_subject}" if re.search(r"\b(matter|matters|important|worth)\b", subject, re.I) else f"Why {low_subject} matters"
        h2s = [why_h[:1].upper() + why_h[1:], "What changes", "Who it helps", close_h]
        body = (
            f"## {h2s[0]}\n\n"
            f"{label} matters because it changes a decision{where}. "
            f"The article should say which decision, and what goes wrong when {low_subject} is skipped.\n\n"
            f"## {h2s[1]}\n\n"
            f"- People can tell what {low_subject} is before they commit\n"
            f"- The useful version is specific{field or ''}, not a general claim\n"
            f"- The page gives one clear next step\n\n"
            f"## {h2s[2]}\n\n"
            f"This is for the person who asked why {low_subject} is worth doing"
            f"{(' in ' + place_name) if place_name else ''}. "
            f"Keep the examples on that question.\n\n"
            f"{close}"
        )
    elif intent == "best":
        h2s = [f"What to look for in {low_subject}", "A short checklist", "What to skip", close_h]
        body = (
            f"## {h2s[0]}\n\n"
            f"Judge {low_subject} by whether it answers the request{where}, not by how many features are listed.\n\n"
            f"## {h2s[1]}\n\n"
            f"- It names {low_subject} in the first lines\n"
            f"- It shows what is included and what is left out\n"
            f"- It fits the reader{field or ''}\n"
            f"- A person can act on it without a second explanation\n\n"
            f"## {h2s[2]}\n\n"
            f"Skip pages that repeat {low_subject} without saying what it does.\n\n"
            f"{close}"
        )
    else:
        h2s = [f"What {low_subject} means", f"What {low_subject} includes", f"How to use {low_subject}", close_h]
        body = (
            f"## {h2s[0]}\n\n"
            f"{label} is the subject of this article{where}. "
            f"The first job is to say what {low_subject} is, in the same words the reader used"
            f"{field or ''}.\n\n"
            f"## {h2s[1]}\n\n"
            f"- A plain definition of {low_subject}\n"
            f"- The pieces that make {low_subject} useful\n"
            f"- Proof or an example, not a stock description\n"
            f"- Who it is for{(' in ' + place_name) if place_name else ''}\n\n"
            f"## {h2s[2]}\n\n"
            f"Use {low_subject} as the thread of the page. "
            f"Open with it, answer it in each section, and end with what the reader should do next.\n\n"
            f"{close}"
        )
    intro = (
        f"{lead}\n\n"
        f"Every section below stays on “{subject.rstrip('?')}”."
    )
    fit_a, fit_b = _industry_fit_lists(who or "local businesses", subject)
    industry_fit = (
        f"We deliver industry-specific website design and iOS and Android mobile app development for {fit_a}.\n\n"
        f"We specialize in custom website design and iOS and Android mobile app development for {fit_b}."
    )
    meta = _fit_words(
        f"{lead.rstrip('.')}" + (f" Written for {place_name}." if place_name and place_name.lower() not in lead.lower() else "."),
        155,
    )
    image_hint = subject.lower()[:80]
    faqs = _faq([
        (f"What is {low_subject}?",
         f"{label} is explained in the first section, in the words used in the topic."),
        (f"Who is {low_subject} for?",
         f"The reader named by the topic{field or ''}{(' in ' + place_name) if place_name else ''}."),
        (f"What should the page include?",
         f"A direct answer about {low_subject}, the parts that belong with it, and one next step."),
        ("Who can build it?",
         "ZeOrbit. Call (619) 724-9517 or visit www.zeorbit.com."),
    ])
    return {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "industry_fit": industry_fit,
        "cta": _soft_cta(subject, city),
        "faqs": faqs,
        "search_intent": intent if intent != "service_pitch" else "explain",
        "image_hint": image_hint,
    }


def topic_driven_article(interp: dict, city: str = "", industry: str = "") -> dict:
    """Build SEO article that answers the interpreted query (not a generic pitch)."""
    intent = interp.get("intent") or "explain"
    low = (interp.get("topic") or "").lower()
    if intent == "compare":
        from services.content_service import _comparison_article_copy

        return _comparison_article_copy(keyword=interp.get("cleaned") or interp.get("topic") or "", city=city)
    if intent == "howto" and re.search(r"restaurant|cafe|café", low):
        return _article_howto(interp, city)
    if intent == "broad" and re.search(r"^(?:restaurants?|cafes?|café)$", low.strip()):
        return _article_broad(interp, city, industry=industry)
    return _reader_article(interp, city, industry)


def _article_howto(interp: dict, city: str = "") -> dict:
    topic = interp.get("topic") or "this topic"
    low = topic.lower()
    place = _place_bit(city)
    seed = f"howto|{low}|{city}".lower()

    if re.search(r"restaurant|cafe|café", low) and re.search(r"customer|more business|more sales|attract|marketing", low):
        title = _pick(seed, [
            f"How Restaurants and Cafes Can Get More Customers{place}",
            f"Practical Ways to Get More Customers for Your Restaurant or Cafe{place}",
            f"How to Attract More Customers to a Restaurant or Cafe{place}",
        ])
        intro = (
            f"Getting more customers{place} is rarely one trick — it is a mix of visibility, trust, "
            f"and a visit people want to repeat.\n\n"
            f"Below are practical steps restaurants and cafes can take without drowning in jargon."
        )
        sections = [
            ("## Fix how people find you locally\n\n"
             "Claim and complete your Google Business Profile, keep hours accurate, add current photos, "
             "and ask happy guests for reviews. Local search is often the first filter before anyone walks in.\n\n"),
            ("## Make the offer obvious online\n\n"
             "Your website or social profile should answer: what you serve, price range, and how to visit or order. "
             "Confusing menus and buried contact info lose people who were ready to choose you.\n\n"),
            ("## Use online ordering or reservations when they fit\n\n"
             "If takeout or bookings matter, make the path short on a phone. Guests abandon long forms. "
             "A simple mobile-friendly flow beats a flashy page that is hard to finish.\n\n"),
            ("## Show up where your guests already scroll\n\n"
             "Post real food, real space, and real hours. Consistency beats viral one-offs. "
             "Promote a weekly special people can remember.\n\n"),
            ("## Turn first visits into repeats\n\n"
             "Loyalty cards, email/SMS offers, or a simple app punch-card only work if the in-person experience "
             "was good. Fix service friction first, then layer rewards.\n\n"),
            ("## Collect and respond to reviews\n\n"
             "Reply to feedback. New guests read how you handle problems as carefully as the star rating.\n\n"),
        ]
        h2s = [
            "Fix how people find you locally",
            "Make the offer obvious online",
            "Use online ordering or reservations when they fit",
            "Show up where your guests already scroll",
            "Turn first visits into repeats",
            "Collect and respond to reviews",
        ]
        meta = (
            f"How can restaurants and cafes get more customers{place}? "
            f"Practical steps for local visibility, online ordering, reviews, and repeat visits."
        )
    else:
        pretty = topic[0].upper() + topic[1:] if topic else "Your Topic"
        # Strip leading how...
        core = re.sub(r"^\s*how(?:\s+(?:can|do|to|does|should))?\s+", "", topic, flags=re.I).strip() or topic
        title = _pick(seed, [
            f"How to {core[:70]}".rstrip("?") if not core.lower().startswith("how") else pretty[:80],
            f"{pretty[:70]}: A Practical Guide",
            f"A Clear Guide: {core[:60]}".rstrip("?"),
        ])
        if title.lower().startswith("how to how"):
            title = f"How to {core[:70]}".rstrip("?")
        intro = (
            f"Here is a practical answer to “{topic.rstrip('?')}”{place} — focused on steps you can act on, "
            f"not filler.\n\n"
            f"Use the sections below as a checklist, then adjust to your situation."
        )
        sections = [
            (f"## Clarify the outcome\n\n"
             f"Restate success in one sentence. If you cannot measure it, the plan will drift.\n\n"),
            (f"## Start with the basics that unblock progress\n\n"
             f"Fix the obvious gaps first: clear messaging, a working contact path, and proof people can trust.\n\n"),
            (f"## Run the smallest useful test\n\n"
             f"Ship one change, measure what guests or customers do next, then iterate.\n\n"),
            (f"## Improve visibility where your audience already looks\n\n"
             f"Search, maps, social, or referrals — pick the channel that matches how people discover you{place}.\n\n"),
            (f"## Keep follow-up simple\n\n"
             f"Reminders, reviews, and a clear next step turn interest into repeat action.\n\n"),
        ]
        h2s = [
            "Clarify the outcome",
            "Start with the basics that unblock progress",
            "Run the smallest useful test",
            "Improve visibility where your audience already looks",
            "Keep follow-up simple",
        ]
        meta = f"Practical guide: {topic.rstrip('?')}{place}. Clear steps you can apply without fluff."

    content = "".join(s[0] if isinstance(s, tuple) else s for s in sections)
    content += (
        f"## When to get help\n\n"
        f"If the bottleneck is a website, ordering flow, or mobile app{place}, a specialist can map the build "
        f"while you stay focused on service. ZeOrbit builds clear sites and apps when that is the missing piece.\n\n"
    )
    h2s = h2s + ["When to get help"]
    faqs = _faq([
        (f"Where should I start?", "Start with the outcome sentence and the highest-friction step guests hit today."),
        (f"How long until I see results?", "Local visibility and reviews often move in weeks; loyalty compounds over months."),
        (f"Do I need ads?", "Not always. Fix findability and the offer first; ads amplify what already works."),
        (f"Can ZeOrbit help?", "Yes — when you need a website or mobile app that supports the plan above. Call 619-724-9517."),
    ])
    return {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": content.strip(),
        "cta": _soft_cta(topic, city),
        "faqs": faqs,
        "search_intent": "howto",
    }


def _article_why(interp: dict, city: str = "") -> dict:
    topic = interp.get("topic") or "this"
    low = topic.lower()
    place = _place_bit(city)
    seed = f"why|{low}|{city}".lower()

    if re.search(r"cafe|café", low) and re.search(r"restaurant|prefer|choose|popular|instead", low):
        title = _pick(seed, [
            "Why People Choose Cafes Instead of Restaurants",
            "Why Cafes Attract Guests Who Skip Full Restaurants",
            f"Why Cafes Are Popular{place}",
        ])
        intro = (
            f"People often choose a cafe over a restaurant when they want speed, a lighter bill, "
            f"or a flexible place to meet — not a full dining occasion{place}.\n\n"
            f"The reasons below explain the preference. A restaurant can still win when the job is a longer meal."
        )
        body = (
            "## Casual atmosphere\n\n"
            "Cafes usually feel easier to enter. Guests do not need a reservation mindset or a long time commitment.\n\n"
            "## Faster visits\n\n"
            "Coffee, pastry, or a light plate can be done in a short window — between errands, meetings, or work blocks.\n\n"
            "## Coffee and light meals\n\n"
            "The menu centers on drinks and simpler food that turns quickly, which matches everyday habits.\n\n"
            "## Social and work-friendly spaces\n\n"
            "Many cafes welcome laptops, short meetups, and solo visits. Restaurants more often optimize for table service meals.\n\n"
            "## Pricing differences\n\n"
            "Average tickets are often lower, so the visit feels lower-risk for a spontaneous stop.\n\n"
            "## Customer experience\n\n"
            "Counter service and clear pickup paths reduce waiting friction when guests are in a hurry.\n\n"
            "## When a restaurant may be better\n\n"
            "Choose a restaurant for celebrations, multi-course meals, table hospitality, or evenings built around dining — "
            "not a quick caffeine stop.\n\n"
        )
        h2s = [
            "Casual atmosphere",
            "Faster visits",
            "Coffee and light meals",
            "Social and work-friendly spaces",
            "Pricing differences",
            "Customer experience",
            "When a restaurant may be better",
        ]
        meta = (
            "Why do people choose cafes instead of restaurants? Atmosphere, speed, menu focus, "
            "pricing, and when a full restaurant is the better fit."
        )
    else:
        core = re.sub(r"^\s*why\s+(?:do|are|is|does|did)?\s*", "", topic, flags=re.I).strip() or topic
        title = _pick(seed, [
            f"Why {core[:70]}".rstrip("?").title() if len(core) < 60 else f"Why This Matters: {core[:50]}",
            f"Reasons Behind {core[:60]}".rstrip("?"),
            topic[:80].rstrip("?") + ("?" if "?" not in topic[:80] else ""),
        ])
        intro = (
            f"“{topic.rstrip('?')}?” is a reasons question{place}. The sections below stay on causes and context — "
            f"not a sales pitch for an unrelated service.\n\n"
            f"Use them to understand the drivers, then decide what to do next."
        )
        body = (
            "## The short answer\n\n"
            f"Most explanations for {core.rstrip('?')} come down to convenience, trust, cost, and whether the experience "
            f"matches what people needed in that moment.\n\n"
            "## Convenience and access\n\n"
            "People pick the option that is easier to reach, understand, and finish — especially on a phone or a short visit.\n\n"
            "## Experience and expectations\n\n"
            "When the atmosphere, speed, or outcome matches the occasion, preference sticks. Mismatch creates churn.\n\n"
            "## Value and perceived risk\n\n"
            "Clear pricing and a predictable result lower the risk of trying something new.\n\n"
            "## Social proof\n\n"
            "Reviews, referrals, and what peers do still shape decisions more than slogans.\n\n"
            "## What this means if you are a business owner\n\n"
            "Design the offer around the reason customers already care about — then make that reason obvious online and in person.\n\n"
        )
        h2s = [
            "The short answer",
            "Convenience and access",
            "Experience and expectations",
            "Value and perceived risk",
            "Social proof",
            "What this means if you are a business owner",
        ]
        meta = f"Why {core.rstrip('?')}{place}: clear reasons, practical context, and what to do with the insight."

    faqs = _faq([
        ("Is one option always better?", "No. Match the option to the job the customer wants done."),
        ("Does location change this?", f"Local habits{place} can shift timing and price sensitivity, but the core reasons usually hold."),
        ("How should I use this as an owner?", "Improve the experience that matches why people choose you — then show it clearly online."),
        ("Can a website or app help?", "Yes, when discovery, ordering, or loyalty is part of the reason people return. ZeOrbit can help with that build."),
    ])
    return {
        "title": (title[:90]).rstrip("?"),
        "h1": (title[:90]).rstrip("?"),
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "cta": _soft_cta(topic, city),
        "faqs": faqs,
        "search_intent": "why",
    }


def _article_what(interp: dict, city: str = "") -> dict:
    topic = interp.get("topic") or "this topic"
    low = topic.lower()
    place = _place_bit(city)
    seed = f"what|{low}|{city}".lower()
    subject = re.sub(r"^\s*what\s+(?:is|are|does|do)\s+", "", topic, flags=re.I).strip(" ?") or topic

    if re.search(r"local seo", low):
        title = _pick(seed, [
            "What Is Local SEO?",
            f"What Local SEO Means for Businesses{place}",
            "Local SEO Explained in Plain English",
        ])
        intro = (
            f"Local SEO is how businesses show up when people search nearby{place} — maps, “near me” queries, "
            f"and city-based service searches.\n\n"
            f"It is not the same as generic national SEO. The goal is to be found by people who can actually visit or call."
        )
        body = (
            "## Local SEO in one sentence\n\n"
            "Help nearby customers find the right business at the right moment, with accurate info and relevant pages.\n\n"
            "## What it usually includes\n\n"
            "- Google Business Profile\n"
            "- Consistent name, address, phone\n"
            "- Location-relevant website pages\n"
            "- Reviews and photos\n"
            "- Clear service/category signals\n\n"
            "## Why it matters\n\n"
            "Many purchases start with a map pack or a local query. If your listing is incomplete, you lose the click.\n\n"
            "## What local SEO is not\n\n"
            "It is not buying random links or stuffing city names into unrelated pages. Relevance and accuracy win.\n\n"
            "## A simple starting checklist\n\n"
            "Verify your profile, fix hours, add photos, align website contact details, and make sure your main services are named plainly.\n\n"
        )
        h2s = [
            "Local SEO in one sentence",
            "What it usually includes",
            "Why it matters",
            "What local SEO is not",
            "A simple starting checklist",
        ]
        meta = "What is local SEO? A plain-English explanation of maps, near-me search, listings, and how local businesses get found."
    else:
        title = _pick(seed, [
            f"What Is {subject.title()}?" if len(subject.split()) <= 6 else f"{subject[:70]} Explained",
            f"Understanding {subject[:60]}",
            f"{subject[:70]}: A Clear Explanation",
        ])
        intro = (
            f"Here is a clear explanation of {subject}{place} — what it is, why people ask, and what to do with the answer.\n\n"
            f"No unrelated service pitch: the article stays on the question you typed."
        )
        body = (
            f"## Plain definition\n\n"
            f"{subject[0].upper() + subject[1:] if subject else 'This topic'} is best understood by the job it does for people — "
            f"what problem it solves and what “done” looks like.\n\n"
            f"## Why people search for it\n\n"
            f"They usually want a usable definition, a comparison point, or the next practical step — not a dictionary dump.\n\n"
            f"## Core pieces to know\n\n"
            f"- Who it is for\n"
            f"- What outcome it promises\n"
            f"- What it requires (time, tools, cost)\n"
            f"- How you know it worked\n\n"
            f"## Common misunderstandings\n\n"
            f"Mixing it up with a similar-sounding topic, or assuming one template fits every business, creates bad decisions.\n\n"
            f"## Practical next step\n\n"
            f"Write one sentence for the outcome you need, then check whether {subject} is the right tool for that outcome.\n\n"
        )
        h2s = [
            "Plain definition",
            "Why people search for it",
            "Core pieces to know",
            "Common misunderstandings",
            "Practical next step",
        ]
        meta = f"What is {subject}? A clear explanation of meaning, why it matters, and a practical next step."

    faqs = _faq([
        (f"What does {subject} mean in simple terms?", f"It is the practical idea behind “{subject}” — the outcome people want when they search it."),
        ("Do I need this for my business?", "Only if it matches a real customer job you need to win."),
        ("Where should I learn more?", "Use the checklist above, then apply it to your own offer and location."),
        ("When does ZeOrbit fit?", "When the next step is a website or app that presents this topic clearly online."),
    ])
    return {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "cta": _soft_cta(subject, city),
        "faqs": faqs,
        "search_intent": "what",
    }


def _article_best(interp: dict, city: str = "") -> dict:
    topic = interp.get("topic") or "best options"
    low = topic.lower()
    place = _place_bit(city)
    seed = f"best|{low}|{city}".lower()

    if re.search(r"restaurant|cafe|café", low) and re.search(r"app|mobile|feature", low):
        title = _pick(seed, [
            "Best Restaurant Mobile App Features",
            f"Must-Have Mobile App Features for Restaurants{place}",
            "Restaurant App Features That Actually Help Guests",
        ])
        intro = (
            f"The best restaurant (or cafe) mobile app features are the ones guests finish using — "
            f"not a long feature list{place}.\n\n"
            f"Below are criteria that matter, and why each one earns a place in a first version."
        )
        body = (
            "## Online ordering\n\nGuests want a short path from menu to paid order on a phone.\n\n"
            "## Reservations or waitlist\n\nUseful when table flow matters; skip it if you are counter-service only.\n\n"
            "## Clear digital menu\n\nPhotos, prices, modifiers, and allergens reduce support calls.\n\n"
            "## Loyalty and rewards\n\nRepeat visits rise when the reward is simple to understand and redeem.\n\n"
            "## Push notifications for offers\n\nUse sparingly for specials and hours changes guests care about.\n\n"
            "## Customer accounts\n\nSaved orders and preferences speed checkout for regulars.\n\n"
            "## Location and hours\n\nMaps, parking notes, and accurate hours prevent failed visits.\n\n"
            "## Reviews and social proof\n\nShow recent feedback where it helps trust without cluttering checkout.\n\n"
            "## Payments\n\nSupport the cards and wallets your guests already use; test failed payments.\n\n"
        )
        h2s = [
            "Online ordering",
            "Reservations or waitlist",
            "Clear digital menu",
            "Loyalty and rewards",
            "Push notifications for offers",
            "Customer accounts",
            "Location and hours",
            "Reviews and social proof",
            "Payments",
        ]
        meta = (
            "Best restaurant mobile app features: ordering, menu, loyalty, notifications, "
            "accounts, location, reviews, and payments — and why each matters."
        )
    else:
        title = _pick(seed, [
            topic[:80].rstrip("?").title() if len(topic) < 60 else f"Best Options for {topic[:50]}",
            f"What to Look For: {topic[:55]}",
            f"A Practical Checklist for {topic[:50]}",
        ])
        intro = (
            f"When people search “{topic.rstrip('?')}”{place}, they want criteria they can use — "
            f"not a random list of brands.\n\n"
            f"Use the points below to judge quality and fit."
        )
        body = (
            "## Start with the job to be done\n\n"
            "Write the outcome the customer must finish. Features that do not serve that job are noise.\n\n"
            "## Look for clarity over novelty\n\n"
            "The best options explain themselves quickly on a phone.\n\n"
            "## Check reliability and support\n\n"
            "A flashy option that breaks checkout or contact paths is not “best.”\n\n"
            "## Prefer measurable results\n\n"
            "Calls, orders, bookings, or repeat visits beat vanity metrics.\n\n"
            "## Fit the operating model\n\n"
            "What works for one business type may be wrong for another. Match tools to how you actually serve people.\n\n"
        )
        h2s = [
            "Start with the job to be done",
            "Look for clarity over novelty",
            "Check reliability and support",
            "Prefer measurable results",
            "Fit the operating model",
        ]
        meta = f"{topic.rstrip('?')}{place}: practical criteria to choose well, without hype."

    faqs = _faq([
        ("Should I build everything at once?", "No. Ship the features that finish the main customer job first."),
        ("How do I prioritize?", "Rank by frequency of use and revenue impact."),
        ("Do small businesses need an app?", "Only if a phone workflow beats a mobile website for your guests."),
        ("Can ZeOrbit build this?", "Yes — share the must-have features and we will map a clear build. Call 619-724-9517."),
    ])
    return {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "cta": _soft_cta(topic, city),
        "faqs": faqs,
        "search_intent": "best",
    }


def _article_broad(interp: dict, city: str = "", industry: str = "") -> dict:
    """Single word / short topic like 'Restaurant' → useful informational article."""
    topic = (interp.get("topic") or "Topic").strip()
    low = topic.lower()
    place = _place_bit(city)
    seed = f"broad|{low}|{city}".lower()
    label = (topic[:1].upper() + topic[1:]) if topic else "Topic"

    if re.search(r"^restaurants?$", low):
        title = _pick(seed, [
            "Restaurants: Types, Service, and Modern Guest Experience",
            f"Understanding Restaurants{place}: Formats, Menus, and Technology",
            "What Makes a Restaurant Work for Guests and Owners",
        ])
        intro = (
            f"A restaurant is built around meals, hospitality, and a visit that usually lasts longer than a quick cafe stop"
            f"{place}.\n\n"
            f"This overview covers formats, guest expectations, operations, and how technology fits — without turning "
            f"the article into an unrelated sales pitch."
        )
        body = (
            "## What a restaurant is\n\n"
            "Restaurants center on prepared food served in a dining environment — from casual rooms to fine dining — "
            "with a clearer meal occasion than a grab-and-go counter.\n\n"
            "## Common restaurant types\n\n"
            "Quick service, fast casual, casual dining, fine dining, and specialty concepts each set different "
            "expectations for speed, price, and service.\n\n"
            "## Menu and service models\n\n"
            "Plated courses, table service, or hybrid counter-plus-table models change staffing and ticket time.\n\n"
            "## Customer experience\n\n"
            "Guests judge hospitality, wait times, clarity of the menu, and whether the visit matched the occasion.\n\n"
            "## Operations owners watch\n\n"
            "Food cost, labor, seating turns, inventory, and consistency across shifts decide whether the concept holds.\n\n"
            "## Technology that actually helps\n\n"
            "Online menus, reservations, ordering, and a simple mobile app can support discovery and repeat visits "
            "when they match how guests already order.\n\n"
            "## Restaurant vs cafe (quick note)\n\n"
            "Cafes usually emphasize coffee, lighter food, and shorter stays. Restaurants usually emphasize fuller meals "
            "and longer hospitality. Many hybrids exist — clarity beats blending both messages.\n\n"
        )
        h2s = [
            "What a restaurant is",
            "Common restaurant types",
            "Menu and service models",
            "Customer experience",
            "Operations owners watch",
            "Technology that actually helps",
            "Restaurant vs cafe (quick note)",
        ]
        meta = (
            "Restaurants explained: types, menus, service, guest experience, operations, "
            "and modern technology — in plain language."
        )
        img_hint = "restaurant dining"
    elif re.search(r"^cafes?$", low) or low in {"café", "cafe"}:
        title = _pick(seed, [
            "Cafes: Atmosphere, Menus, and Why Guests Return",
            f"What Defines a Cafe{place}",
            "Cafe Basics for Guests and Owners",
        ])
        intro = (
            f"A cafe is typically built for coffee, lighter food, and flexible visits{place} — "
            f"solo work, short meetups, or a quick bite.\n\n"
            f"Here is a clear overview of what cafes are and how they differ from fuller restaurant experiences."
        )
        body = (
            "## What a cafe is\n\n"
            "Cafes emphasize beverages and simpler food with a come-and-go rhythm.\n\n"
            "## Atmosphere\n\n"
            "Casual seating, counter service, and a space that can handle short stays or light laptop time.\n\n"
            "## Menu focus\n\n"
            "Coffee programs, pastry, and lighter plates that turn faster than multi-course dining.\n\n"
            "## Guest motivations\n\n"
            "Speed, comfort, and a lower-commitment visit than a full restaurant meal.\n\n"
            "## Operations\n\n"
            "Throughput, beverage quality, and morning/afternoon dayparts often matter more than dinner theater.\n\n"
            "## Digital touchpoints\n\n"
            "Mobile ordering, loyalty, and clear hours online help regulars return without friction.\n\n"
        )
        h2s = [
            "What a cafe is",
            "Atmosphere",
            "Menu focus",
            "Guest motivations",
            "Operations",
            "Digital touchpoints",
        ]
        meta = "Cafes explained: atmosphere, menus, guest habits, operations, and useful digital tools."
        img_hint = "cafe coffee"
    else:
        who = (industry or "").strip() or "a local business"
        who_l = who.lower()
        title = f"{label} for {who}{place}"
        intro = (
            f"{label} for {who_l} means the work is shaped around that field"
            f"{place}, not copied from a layout that could fit any business.\n\n"
            f"People looking for {label.lower()} want the actual {who_l} service, who it helps, and how to get started."
        )
        body = (
            f"## What {label.lower()} means for {who_l}\n\n"
            f"In {who_l}, {label.lower()} is the difference between a generic presence and one built for the people you serve. "
            f"A visitor should recognize the field right away: the services, the setting, and the result they came for"
            f"{place}. If the same page could describe a restaurant, a contractor, or a clinic, it is not custom to {who_l} yet.\n\n"
            f"## Who it is for\n\n"
            f"It is for {who_l} teams whose current site hides the work, and for customers who already know the kind of help they need. "
            f"Those customers compare a few options. They choose the one that explains the service in plain language and shows a clear way to reach the business.\n\n"
            f"## How it works in practice\n\n"
            f"A {label.lower()} project for {who_l} starts with the services people ask about. "
            f"Those services become the headlines. Photos show the real setting. Hours, location, and a phone number stay easy to find on a phone. "
            f"Buttons and forms match how the business actually takes the next step, whether that is a call, a visit, or a booking"
            f"{place}.\n\n"
            f"## What good looks like\n\n"
            f"On a good {who_l} page, a person can say what you do, where you do it, and how to reach you without hunting. "
            f"The words stay specific to {who_l}. Each section answers one question, then points to the next.\n\n"
            f"## Common mistakes\n\n"
            f"Copying another {who_l} business and changing only the name. Using photos from a different industry. "
            f"Adding extra tools before the basic facts are easy to find. Talking about {label.lower()} in the abstract "
            f"and never naming the {who_l} services customers came to read about.\n\n"
            f"## Next step\n\n"
            f"ZeOrbit builds websites and apps for {label.lower()} in {who_l}{place}, starting from the services your customers already look for. "
            f"Call (619) 724-9517 or visit www.zeorbit.com.\n\n"
        )
        h2s = [
            f"What {label.lower()} means for {who.lower()}",
            "Who it is for",
            "How it works in practice",
            "What good looks like",
            "Common mistakes",
            "Next step",
        ]
        meta = (f"{label} for {who}{place}. What it covers, who it is for, and how ZeOrbit builds it.")[:160]
        img_hint = f"{who} {label}".lower()

    faqs = _faq([
        (f"What does {label.lower()} mean here?",
         f"It means the site is built around {(industry or 'the business').strip().lower()} services and the people who need them."),
        (f"Who is this for?",
         f"{(industry or 'Local').strip()} teams, and customers comparing options before they call or book."),
        (f"Why mention the city?",
         f"Readers{place} expect the service, the area, and a way to reach you on the same page."),
        (f"How does ZeOrbit help?",
         f"ZeOrbit builds the website or app. Call (619) 724-9517."),
    ])
    out = {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "cta": _soft_cta(label, city),
        "faqs": faqs,
        "search_intent": "broad",
        "image_hint": img_hint,
    }
    return out


def _article_explain(interp: dict, city: str = "") -> dict:
    """Fallback: answer the cleaned query without ZeOrbit website pitch templates."""
    topic = interp.get("topic") or interp.get("cleaned") or "your topic"
    place = _place_bit(city)
    title = topic[:80].rstrip("?").strip()
    if len(title) < 8:
        title = f"About {title}"
    # Prefer sentence case title without repeating the raw dump
    if len(title) > 70:
        title = " ".join(title.split()[:10])
    intro = (
        f"Here is a useful answer to “{topic.rstrip('?')}”{place}.\n\n"
        f"The sections below stay on that request: what it means, what matters, and what to do next."
    )
    body = (
        f"## Direct answer\n\n"
        f"Treat the request as a real question. Identify the outcome someone wants, the constraints they have, "
        f"and the smallest explanation that would help them act.\n\n"
        f"## What matters most\n\n"
        f"- Relevance to the words they used\n"
        f"- A practical next step\n"
        f"- Clear language over buzzwords\n\n"
        f"## How to apply it\n\n"
        f"Write the outcome in one sentence, list what you already know, then fill the single biggest gap.\n\n"
        f"## Related checks\n\n"
        f"If a comparison, how-to, or feature list would answer better, ask that more specific question next.\n\n"
    )
    h2s = ["Direct answer", "What matters most", "How to apply it", "Related checks"]
    meta = f"A clear answer to “{topic.rstrip('?')}”{place} — practical, on-topic, and easy to act on."
    return {
        "title": title[:90],
        "h1": title[:90],
        "meta_description": re.sub(r"\s+", " ", meta).strip()[:230],
        "h2s": h2s,
        "intro": intro.strip(),
        "content": body.strip(),
        "cta": _soft_cta(topic, city),
        "faqs": _faq([
            ("Does this match my question?", "Yes — it is built from the topic field you entered, not from industry defaults."),
            ("Can I add a location?", "Location can add context but should not replace the topic."),
            ("What if I meant something else?", "Rephrase with how / why / vs / best to lock the intent."),
            ("Can ZeOrbit help after this?", "When you need a website or app aligned to this topic — call 619-724-9517."),
        ]),
        "search_intent": "explain",
    }


def image_hint_for_interp(interp: dict) -> str:
    """Stock focus string from interpreted topic (never industry hijack)."""
    intent = interp.get("intent")
    low = (interp.get("topic") or "").lower()
    if intent == "compare" or (re.search(r"restaurant", low) and re.search(r"cafe|café", low)):
        return "restaurant cafe dining interior"
    if re.search(r"\bcafe|café\b", low):
        return "cafe coffee interior"
    if re.search(r"\brestaurant", low):
        return "restaurant dining interior"
    if interp.get("wants_app") or re.search(r"\bapp\b", low):
        return "mobile app phone"
    if re.search(r"\bseo\b", low):
        return "seo analytics dashboard laptop"
    hint = (interp.get("image_hint") or interp.get("topic") or "business").strip()
    return hint[:80]
