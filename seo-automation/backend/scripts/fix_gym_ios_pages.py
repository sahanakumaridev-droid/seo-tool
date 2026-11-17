"""Rewrite published gym iOS pages so copy and photos match the topic."""
import asyncio

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from db import AsyncSessionLocal, PageRecord

U = "https://images.unsplash.com/{}?auto=format&fit=crop&w=1600&q=80"

# Distinct gym / training photos. One hero per page.
HEROES = [
    "photo-1534438327276-14e5300c3a48",
    "photo-1517836357463-d25dfeac3438",
    "photo-1571902943202-507ec2618e8f",
    "photo-1518611012118-696072aa579a",
    "photo-1540497077202-7c8a3999166f",
    "photo-1571019614242-c5c5dee9f50b",
    "photo-1583454110551-21f2fa2afe61",
    "photo-1599058917212-d750089bc07e",
    "photo-1574680096145-d05b474e2155",
    "photo-1549060279-7e168fcee0c2",
    "photo-1550345332-09e3ac987658",
    "photo-1526506118085-60ce8714f8c5",
    "photo-1517838277536-f5f99be501cd",
    "photo-1579758629938-03607ccdbaba",
    "photo-1605296867304-46d5465a13f1",
    "photo-1581009146145-b5ef050c2e1e",
    "photo-1434494878577-86c23bcb06b9",
    "photo-1476480862126-209bfaa8edc8",
    "photo-1517963879433-6ad2b056d712",
    "photo-1593079831268-3381b0db4a77",
    "photo-1576678927484-cc907957088c",
    "photo-1541534741688-6078c6bfb5c5",
    "photo-1599058945522-28d584b6f14f",
    "photo-1517960413843-0aee8e2b3285",
]

LOCAL = [
    "https://zeorbit.com/topics/gym-ios/gym-ios-hero.jpg",
    "https://zeorbit.com/topics/gym-ios/gym-ios-workout.jpg",
    "https://zeorbit.com/topics/gym-ios/gym-ios-class.jpg",
    "https://zeorbit.com/topics/gym-ios/gym-ios-membership.jpg",
    "https://zeorbit.com/topics/gym-ios/gym-ios-metrics.jpg",
    "https://zeorbit.com/topics/gym-ios/gym-ios-plan.jpg",
]

# slug, place name, one local detail so the body is not a clone
PAGES = [
    ("ios-app-development-for-gyms-in-aviara", "Aviara", "golf-course and resort neighborhoods where members expect a polished booking experience"),
    ("ios-app-development-for-gyms-in-la-costa", "La Costa", "racquet, spa, and training clubs that juggle court times with gym sessions"),
    ("ios-app-development-for-gyms-in-downtown-carlsbad", "Downtown Carlsbad", "boutique studios near State Street that fill classes from walk-ins and app bookings"),
    ("ios-app-development-for-gyms-in-olde-carlsbad", "Olde Carlsbad", "neighborhood gyms that rely on repeat members rather than tourist traffic"),
    ("ios-app-development-for-gyms-in-carlsbad-village", "Carlsbad Village", "studios a short walk from the village shops, where class reminders keep the schedule full"),
    ("ios-app-development-for-gyms-in-vista", "Vista", "family gyms and training barns that need simple membership and class tools"),
    ("ios-app-development-for-gyms-in-solana-beach", "Solana Beach", "small coastal studios where peak hours sell out without a waitlist"),
    ("ios-app-development-for-gyms-in-santee", "Santee", "community gyms serving members who train before work and want a fast check-in"),
    ("ios-app-development-for-gyms-in-san-marcos", "San Marcos", "gyms near campus and new housing that sign up younger members on iPhone"),
    ("ios-app-development-for-gyms-in-san-diego", "San Diego", "multi-location gyms that need one iPhone app for several neighborhoods"),
    ("ios-app-development-for-gyms-in-poway", "Poway", "suburban training gyms where parents book youth sessions and adults book after work"),
    ("ios-app-development-for-gyms-in-oceanside", "Oceanside", "beach-town gyms that mix open gym, classes, and personal training on one schedule"),
    ("ios-app-development-for-gyms-oceansidein", "Oceanside", "Oceanside gyms that still take sign-ups by text instead of an iPhone membership app"),
    ("ios-app-development-for-gyms-in-national-city", "National City", "local gyms that need bilingual-friendly screens and a clear path to buy a membership"),
    ("ios-app-development-for-gyms-in-lemon-grove", "Lemon Grove", "independent gyms that cannot afford a generic chain app that ignores their class list"),
    ("ios-app-development-for-gyms-in-la-mesa", "La Mesa", "village gyms where members want to see the weekly class board on their phone"),
    ("ios-app-development-for-gyms-in-imperial-beach", "Imperial Beach", "compact gyms near the pier that turn drop-ins into members with a simple iPhone signup"),
    ("ios-app-development-for-gyms-in-escondido", "Escondido", "larger floor plans that need trainer schedules and membership freezes in one app"),
    ("ios-app-development-for-gyms-in-encinitas", "Encinitas", "yoga, strength, and surf-fitness studios that share one booking problem"),
    ("ios-app-development-for-gyms-el-cajon", "El Cajon", "high-volume gyms that need barcode or phone check-in at the front desk"),
    ("ios-app-development-for-gyms-in-del-mar", "Del Mar", "low-volume premium training where clients expect private session booking on iPhone"),
    ("ios-app-development-for-gyms-in-coronado", "Coronado", "island gyms serving residents and short-stay guests who still need a membership option"),
    ("ios-app-development-for-gyms-in-chula-vista", "Chula Vista", "growing gyms that add a second location and need the same member login in both"),
    ("ios-app-development-for-gyms-in-carlsbad", "Carlsbad", "gyms across Carlsbad that want class booking, not another generic fitness template"),
]


def img(url, alt, featured=False):
    return {
        "url": url,
        "filename": url.rsplit("/", 1)[-1].split("?")[0] + ".jpg",
        "mime_type": "image/jpeg",
        "alt_text": alt,
        "title": alt,
        "caption": alt,
        "description": alt,
        "is_featured": featured,
    }


def build(place, detail, hero, mid, foot):
    h1 = f"iOS App Development for Gyms in {place}"
    title = f"iOS App Development for Gyms in {place}"
    meta = (
        f"iPhone app development for gyms in {place}. Class booking, memberships, "
        f"and trainer schedules from ZeOrbit. Call (619) 724-9517."
    )
    intro = (
        f"Gym owners in {place} lose sign-ups when the only way to book a class is a phone call or a paper schedule. "
        f"An iOS app puts membership, class times, and trainer booking on the iPhone your members already carry.\n\n"
        f"This page is about iPhone app development for gyms in {place} — {detail}."
    )
    h2s = [
        f"What a gym iPhone app should do in {place}",
        "Memberships, classes, and trainer booking",
        f"How ZeOrbit builds the iOS app for a {place} gym",
    ]
    content = (
        f"## {h2s[0]}\n\n"
        f"Members in {place} open their phone to see if a class has space. "
        f"The app should show today’s schedule, a waitlist, and a one-tap way to join. "
        f"It should also work for the front desk, so staff are not retyping the same name into a spreadsheet.\n\n"
        f"## {h2s[1]}\n\n"
        f"A useful gym app covers the jobs the desk already does: freeze a membership, sell a class pack, "
        f"assign a trainer, and send a reminder before the session. "
        f"For {place}, that matters because {detail}.\n\n"
        f"## {h2s[2]}\n\n"
        f"ZeOrbit designs and builds the iOS app around your gym, not a chain template. "
        f"We map your class types, your membership rules, and how trainers get paid for sessions. "
        f"Then we ship an iPhone app your members can download, with a clear path to contact the gym.\n\n"
        f"Call ZeOrbit at (619) 724-9517 or visit [zeorbit.com](https://www.zeorbit.com/) to talk through an iOS app for your {place} gym."
    )
    faqs = [
        {
            "question": f"Can ZeOrbit build an iPhone app for my gym in {place}?",
            "answer": f"Yes. ZeOrbit builds iOS apps for gyms that need class booking, memberships, and trainer schedules in {place}.",
        },
        {
            "question": "Does the app replace our front desk?",
            "answer": "No. The app takes booking and membership questions off the phone so staff can spend time with people who are in the gym.",
        },
        {
            "question": "Can members book personal training on iPhone?",
            "answer": f"Yes. Trainer availability, session requests, and reminders can live in the same iOS app as the {place} class schedule.",
        },
        {
            "question": "How do I start?",
            "answer": "Call ZeOrbit at (619) 724-9517 or visit www.zeorbit.com. We start from your current class list and membership rules.",
        },
    ]
    alt_h = f"Gym floor used as the visual for an iOS app project in {place}"
    alt_m = f"Strength training photo for a {place} gym iPhone app"
    alt_f = f"Fitness session photo for gym app development in {place}"
    return {
        "title": title,
        "meta_description": meta[:160],
        "h1": h1,
        "h2s": h2s,
        "h3s": ["Class schedule", "Memberships", "Trainer booking", "iPhone App Store"],
        "intro": intro,
        "content": content,
        "faqs": faqs,
        "cta": f"Call ZeOrbit at (619) 724-9517 to plan an iOS app for your gym in {place}.",
        "industry": "Gyms",
        "business_type": "iOS app development for gyms",
        "focus_keyword": f"iOS app development for gyms in {place}",
        "featured_image_url": hero,
        "footer_image_url": foot,
        "in_content_images": [
            img(hero, alt_h, True),
            img(mid, alt_m, False),
            img(foot, alt_f, False),
        ],
        "keywords": {
            "primary": f"ios app development for gyms in {place}".lower(),
            "secondary": [
                f"gym iphone app {place}".lower(),
                "class booking app",
                "gym membership app",
            ],
            "long_tail": [f"ios app development for gyms in {place}".lower()],
            "near_me": [f"gym app developer near {place}".lower()],
            "user_questions": [f["question"] for f in faqs],
        },
    }


async def main():
    updated = []
    missing = []
    async with AsyncSessionLocal() as session:
        for i, (slug, place, detail) in enumerate(PAGES):
            row = (await session.execute(select(PageRecord).where(PageRecord.slug == slug))).scalar_one_or_none()
            if not row:
                missing.append(slug)
                continue
            hero = U.format(HEROES[i])
            mid = LOCAL[i % len(LOCAL)]
            foot = U.format(HEROES[(i + 7) % len(HEROES)])
            block = dict(row.seo_block or {})
            block.update(build(place, detail, hero, mid, foot))
            block["slug"] = slug
            block["city"] = block.get("city") or place
            row.seo_block = block
            flag_modified(row, "seo_block")
            updated.append(slug)
        await session.commit()
    print("updated", len(updated))
    for s in updated:
        print(" ", s)
    print("missing", missing)


if __name__ == "__main__":
    asyncio.run(main())
