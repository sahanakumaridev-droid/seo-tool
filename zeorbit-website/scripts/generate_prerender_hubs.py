#!/usr/bin/env python3
"""Write unique first-byte HTML for marketing hubs (crawlers that skip JS)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "public"
SITE = "https://zeorbit.com"

HUBS = [
    {
        "path": "website-designing",
        "title": "Website Design — WordPress, Shopify, Wix & Squarespace | ZeOrbit",
        "h1": "Website design for U.S. businesses",
        "desc": "Custom website design and development for U.S. businesses. WordPress, Shopify, Wix, Squarespace, redesigns, and Master Care from ZeOrbit in San Diego.",
        "body": (
            "ZeOrbit designs and builds WordPress, Shopify, Wix, and Squarespace websites "
            "from San Diego, CA. Call 619-724-9517. Address: 4231 Balboa Avenue, Suite 1340, San Diego, CA 92117."
        ),
    },
    {
        "path": "mobile-apps",
        "title": "Mobile App Development — iOS & Android | ZeOrbit",
        "h1": "iOS and Android app development",
        "desc": "ZeOrbit designs and builds iOS and Android apps — native and cross-platform — from prototype to App Store and Google Play launch.",
        "body": (
            "ZeOrbit builds native and cross-platform mobile apps for U.S. companies. "
            "San Diego HQ. Phone 619-724-9517. Email info@zeorbit.com."
        ),
    },
    {
        "path": "custom-software",
        "title": "Custom Software & Internal Tools | ZeOrbit",
        "h1": "Custom software and internal tools",
        "desc": "Custom software, dashboards, automation, and portals built around how your U.S. business actually runs. Architecture, build, and ongoing support.",
        "body": (
            "ZeOrbit designs custom software, dashboards, and portals for U.S. businesses. "
            "Meet in San Diego or work remotely nationwide."
        ),
    },
    {
        "path": "seo-ppc",
        "title": "SEO, GEO, PPC & Google Ads | ZeOrbit",
        "h1": "SEO, local SEO, and Google Ads",
        "desc": "Technical SEO, local SEO, content, GEO, PPC, and Google Ads so U.S. businesses get found and chosen. Strategy, execution, and reporting from ZeOrbit.",
        "body": (
            "ZeOrbit runs technical SEO, local SEO, and Google Ads for U.S. brands. "
            "This is a service page, not a Maps listing — for near-me searches see /web-designer-near-me."
        ),
    },
    {
        "path": "contact",
        "title": "Contact ZeOrbit — Websites, Apps & Growth",
        "h1": "Contact ZeOrbit",
        "desc": "Talk with ZeOrbit about a website, mobile app, SEO, or custom software project. Call +1 (619) 724-9517 or email info@zeorbit.com. San Diego, CA 92117.",
        "body": (
            "Call 619-724-9517 or email info@zeorbit.com. "
            "ZeOrbit, 4231 Balboa Avenue, Suite 1340, San Diego, CA 92117."
        ),
    },
    {
        "path": "blog",
        "title": "Insights — Website, App & SEO Guides | ZeOrbit",
        "h1": "ZeOrbit insights",
        "desc": "Practical guides on websites, WordPress, Shopify, mobile apps, SEO, and digital growth from the ZeOrbit team.",
        "body": "Guides on websites, mobile apps, and SEO from the ZeOrbit team in San Diego.",
    },
    {
        "path": "portfolio",
        "title": "Our Work — ZeOrbit Web, App & Brand Portfolio",
        "h1": "ZeOrbit portfolio",
        "desc": "Selected websites, mobile apps, flyers, and logos designed and built by ZeOrbit for businesses across California and beyond.",
        "body": "Selected websites, apps, and brand work by ZeOrbit for California and U.S. clients.",
    },
    {
        "path": "privacy-policy",
        "title": "Privacy Policy — ZeOrbit",
        "h1": "Privacy policy",
        "desc": "How ZeOrbit collects, uses, and protects personal information on zeorbit.com.",
        "body": "How ZeOrbit collects and uses personal information on zeorbit.com. Contact info@zeorbit.com.",
    },
    {
        "path": "areas",
        "title": "Areas We Serve — ZeOrbit",
        "h1": "Areas ZeOrbit serves",
        "desc": "ZeOrbit serves San Diego, El Cajon, Los Angeles, Orange County, and clients nationwide with websites, apps, SEO, and custom software.",
        "body": "ZeOrbit is based in San Diego and serves California and the United States.",
    },
    {
        "path": "areas/san-diego",
        "title": "San Diego Web Design & Digital Agency — ZeOrbit",
        "h1": "Web design in San Diego",
        "desc": "San Diego web design, WordPress, Shopify, apps, and SEO from ZeOrbit. 5.0 Google rating. Call 619-724-9517.",
        "body": (
            "ZeOrbit is a San Diego web design company at 4231 Balboa Avenue, Suite 1340. "
            "WordPress, Shopify, mobile apps, and local SEO. Call 619-724-9517."
        ),
    },
    {
        "path": "areas/el-cajon",
        "title": "El Cajon Web Design — ZeOrbit",
        "h1": "Web design for El Cajon businesses",
        "desc": "Website design, apps, and SEO for El Cajon and East County from ZeOrbit in San Diego.",
        "body": "ZeOrbit serves El Cajon with websites, apps, and SEO from our San Diego office.",
    },
    {
        "path": "areas/los-angeles",
        "title": "Los Angeles Web Design — ZeOrbit",
        "h1": "Websites and apps for Los Angeles brands",
        "desc": "ZeOrbit builds websites, mobile apps, and SEO programs for Los Angeles companies, remotely from San Diego.",
        "body": "Los Angeles companies work with ZeOrbit remotely for websites, apps, and SEO.",
    },
    {
        "path": "areas/orange-county",
        "title": "Orange County Web Design — ZeOrbit",
        "h1": "Web design in Orange County",
        "desc": "Website design, Shopify, and SEO for Orange County businesses from ZeOrbit.",
        "body": "ZeOrbit serves Orange County with website design, apps, and SEO.",
    },
    {
        "path": "areas/new-york",
        "title": "New York Web Design — ZeOrbit",
        "h1": "Websites and software for New York companies",
        "desc": "U.S. remote website, app, and software work for New York companies from ZeOrbit.",
        "body": "New York teams hire ZeOrbit for websites, mobile apps, and custom software.",
    },
]


def page_html(h: dict) -> str:
    path = h["path"]
    url = f"{SITE}/{path}"
    title = h["title"]
    desc = h["desc"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <link rel="canonical" href="{url}" />
  <link rel="alternate" type="text/plain" title="LLM information" href="/llms.txt" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="ZeOrbit" />
  <script type="application/ld+json">
  {json.dumps({"@context":"https://schema.org","@type":"WebPage","name":title,"url":url,"description":desc,"isPartOf":{"@type":"WebSite","name":"ZeOrbit","url":f"{SITE}/"}})}
  </script>
</head>
<body>
  <p><a href="{SITE}/">ZeOrbit home</a></p>
  <h1>{h["h1"]}</h1>
  <p>{h["body"]}</p>
  <p>Phone: <a href="tel:+16197249517">619-724-9517</a> ·
     Email: <a href="mailto:info@zeorbit.com">info@zeorbit.com</a></p>
  <nav>
    <a href="{SITE}/website-designing">Website design</a>
    <a href="{SITE}/web-designer-near-me">Web designer near me</a>
    <a href="{SITE}/mobile-apps">Mobile apps</a>
    <a href="{SITE}/seo-ppc">SEO</a>
    <a href="{SITE}/contact">Contact</a>
    <a href="{SITE}/llms.txt">llms.txt</a>
  </nav>
</body>
</html>
"""


def main() -> None:
    for h in HUBS:
        dest = ROOT / h["path"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page_html(h), encoding="utf-8")
        print(dest)

    nf = ROOT / "404.html"
    nf.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Page not found — ZeOrbit</title>
  <meta name="robots" content="noindex,follow" />
  <link rel="canonical" href="https://zeorbit.com/" />
</head>
<body>
  <h1>Page not found</h1>
  <p>This URL is not a published ZeOrbit page.</p>
  <p><a href="https://zeorbit.com/">Go to the homepage</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(nf)


if __name__ == "__main__":
    main()
