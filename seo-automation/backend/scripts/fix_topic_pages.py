"""Give published topic pages matching copy and distinct photos."""
import asyncio

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from db import AsyncSessionLocal, PageRecord

U = "https://images.unsplash.com/{}?auto=format&fit=crop&w=1600&q=80"

TINT = [
    "photo-1492144534655-ae79c964c9d7",
    "photo-1503376780353-7e6692767b70",
    "photo-1494976388531-d1058494cdd8",
    "photo-1542362567-48480f9d5a0f",
    "photo-1502877338535-766e1452684a",
    "photo-1511919884226-fd3cad34687c",
    "photo-1489824904134-891ab64532f1",
    "photo-1552519507-da3b142c6e3d",
    "photo-1549924231-f129b911e442",
    "photo-1493238792000-8113da705763",
    "photo-1449965408869-eaa3f722e40d",
    "photo-1485291571150-772bcfc10da5",
    "photo-1619642751034-765dfdf7c58e",
    "photo-1605559424843-9e4c228bf1c2",
    "photo-1549317661-bd32c8ce0db2",
    "photo-1550355291-bbee04a92027",
    "photo-1563720223185-11003d516935",
    "photo-1617531653332-bd46c24f2068",
    "photo-1616422285623-13ff0162193c",
]
WEB = [
    "photo-1467232004584-a241de8bcf5d",
    "photo-1460925895917-afdab827c52f",
    "photo-1545235617-9465d2a55698",
    "photo-1522542550221-31fd19575a2d",
    "photo-1581291518633-83b4ebd1d83e",
    "photo-1559028012-481c04fa702d",
    "photo-1486312338219-ce68d2c6f44d",
    "photo-1547658719-da2b51169166",
    "photo-1558655146-9f40138edfeb",
    "photo-1561070791-2526d30994b5",
    "photo-1507238691740-187a5b1d37b8",
    "photo-1531403009284-440f080d1e12",
    "photo-1499951360447-b19be8fe80f5",
    "photo-1555421689-491a97ff2040",
    "photo-1516321318423-f06f85e504b3",
    "photo-1432888498266-38ffec3eaf0a",
    "photo-1551288049-bebda4e38f71",
    "photo-1522199755839-a2bacb67c546",
    "photo-1551434678-e076c223a692",
    "photo-1586717791821-3f44a563fa4c",
    "photo-1618761714954-0b8cd0026356",
    "photo-1481487196290-c152efe700ba",
    "photo-1593720216276-0caa6452c8d0",
    "photo-1561070791-0369aee323b7",
]
CODE = [
    "photo-1498050108023-c5249f4df085",
    "photo-1461749280684-dccba630e2f6",
    "photo-1517694712202-14dd9538aa97",
    "photo-1555066931-4365d14bab8c",
    "photo-1488590528505-98d2b5aba04b",
    "photo-1542831371-29b0f74f9713",
    "photo-1515879218367-8466d910aaa4",
    "photo-1605379399642-870262d3d051",
    "photo-1504639725590-34d0984388bd",
    "photo-1555949963-aa79dcee981c",
    "photo-1571171637578-41bc2dd41cd2",
    "photo-1627398242454-45a1465c2479",
    "photo-1633356122544-f134324a6cee",
    "photo-1587620962725-abab7fe55159",
    "photo-1531297484001-80022131f5a1",
    "photo-1517430816045-df4b7de11d1d",
    "photo-1496171367470-9ed9a91ea931",
    "photo-1483058712412-4245e9b90334",
    "photo-1550439062-609e1531270e",
    "photo-1593720213428-28a5b9e94613",
    "photo-1519389950473-47ba0277781c",
    "photo-1556761175-5973dc0f32e7",
    "photo-1522202176988-66273c2fd55f",
    "photo-1600880292203-757bb62b4baf",
    "photo-1454165804606-c3d57bc86b40",
    "photo-1542744173-8e7e53415bb0",
    "photo-1552664730-d307ca884978",
    "photo-1497366216548-37526070297c",
    "photo-1497366811353-6870744d04b2",
    "photo-1486406146926-c627a92ad1ab",
    "photo-1559136555-9303baea8ebd",
    "photo-1542744094-3a31f272c490",
]

TINT_SLUGS = """
professional-website-designer-window-tinting-businesses-in-pico-rivera
professional-website-designer-window-tinting-businesses-in-burbank
professional-website-designer-window-tinting-businesses-in-inglewood
professional-website-designer-window-tinting-businesses-in-lynwood
why-every-window-tinting-business-needs-a-professional-website-san-marino
professional-website-designer-window-tinting-businesses-in-rosemead
professional-website-designer-window-tinting-businesses-in-universal-city
professional-website-designer-window-tinting-businesses-in-pasadena
why-every-window-tinting-business-needs-a-professional-website-glendale
professional-website-designer-window-tinting-businesses-in-beverly-hills
professional-website-designer-window-tinting-businesses-in-montebello
why-every-window-tinting-business-needs-a-professional-website-south-gate
professional-website-designer-window-tinting-businesses-in-west-hollywood
professional-website-designer-window-tinting-businesses-in-alhambra
professional-website-designer-window-tinting-businesses-in-monterey-park
professional-website-designer-window-tinting-businesses-in-south-pasadena
professional-website-designer-window-tinting-businesses-in-bell
professional-website-designer-window-tinting-businesses-in-bell-gardens
website-designer-window-tinting-businesses-in-huntington-park
website-designer-for-window-tinting-businesses-in-los-angeles
professional-website-designer-window-tinting-business-in-maywood
""".split()

NEW_SLUGS = """
new-business-website-design-hosp-grove
new-business-website-design-kelly-ranch
new-business-website-design-terramar
new-business-website-design-poinsettia
new-business-website-design-robertson-ranch
new-business-website-design-rancho-carrillo
new-business-website-design-calavera-hills-village
new-business-website-design-calavera-hills
new-business-website-design-bressi-ranch
new-business-website-design-aviara
new-business-website-design-carlsbad-village
new-business-website-design-downtown-carlsbad
new-business-website-design-olde-carlsbad
new-business-website-design-la-costa
new-business-website-design-carlsbad
website-designing-in-carlsbad-village
""".split()

WP_SLUGS = """
wordpress-website-maintenance-san-marino
wordpress-website-maintenance-in-alhambra
wordpress-website-maintenance-in-south-pasadena
wordpress-website-maintenance-downtown-in-south-pasadena
wordpress-website-maintenance-in-bell-gardens-village
wordpress-website-maintenance-in-north-bell-gardens
wordpress-website-maintenance-in-bell-gardens-heights
wordpress-website-maintenance-in-downtown-bell-gardens
wordpress-website-maintenance-in-gardena
wordpress-website-maintenance-in-los-angeles-village
wordpress-website-maintenance-in-north-los-angeles
wordpress-website-maintenance-in-los-angeles-heights
wordpress-website-maintenance-downtown-los-angeles
wordpress-website-maintenance-compton
wordpress-website-maintenance-maywood
wordpress-website-maintenance-huntington-park-village
wordpress-website-maintenance-north-huntington-park
wordpress-website-maintenance-huntington-park-heights
wordpress-website-maintenance-downtown-huntington-park
wordpress-website-maintenance-downey
wordpress-website-maintenance-montebello
wordpress-website-maintenance-lynwood
wordpress-website-maintenance-los-angeles
wordpress-website-maintenance-south-gate
wordpress-website-maintenance-huntington-park
wordpress-website-maintenance-bell
wordpress-website-maintenance-bell-gardens
wordpress-website-maintenance-maywood-village
wordpress-website-maintenance-north-maywood
wordpress-website-maintenance-maywood-heights
""".split()

REDESIGN_SLUGS = """
5-signs-it-s-time-to-redesign-your-business-website-los-angeles-heights
5-signs-it-s-time-to-redesign-your-business-website-huntington-park-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-los-angeles
5-signs-it-s-time-to-redesign-your-business-website-downtown-huntington-park
5-signs-it-s-time-to-redesign-your-business-website-north-huntington-park
5-signs-it-s-time-to-redesign-your-business-website-huntington-park-heights
5-signs-it-s-time-to-redesign-your-business-website-los-angeles-village
5-signs-it-s-time-to-redesign-your-business-website-bell-gardens-heights
5-signs-it-s-time-to-redesign-your-business-website-downtown-south-pasadena
5-signs-it-s-time-to-redesign-your-business-website-bell-gardens-village
5-signs-it-s-time-to-redesign-your-business-website-north-bell-gardens
5-signs-it-s-time-to-redesign-your-business-website-south-pasadena-heights
5-signs-it-s-time-to-redesign-your-business-website-downtown-monterey-park
5-signs-it-s-time-to-redesign-your-business-website-monterey-park-heights
5-signs-it-s-time-to-redesign-your-business-website-north-monterey-park
5-signs-it-s-time-to-redesign-your-business-website-monterey-park-village
5-signs-it-s-time-to-redesign-your-business-website-bell-heights
5-signs-it-s-time-to-redesign-your-business-website-bell-village
5-signs-it-s-time-to-redesign-your-business-website-north-alhambra
5-signs-it-s-time-to-redesign-your-business-website-downtown-alhambra
5-signs-it-s-time-to-redesign-your-business-website-alhambra-heights
5-signs-it-s-time-to-redesign-your-business-website-south-gate-heights
5-signs-it-s-time-to-redesign-your-business-website-south-gate-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-montebello
5-signs-it-s-time-to-redesign-your-business-website-montebello-heights
5-signs-it-s-time-to-redesign-your-business-website-montebello-village
5-signs-it-s-time-to-redesign-your-business-website-west-hollywood-village
5-signs-it-s-time-to-redesign-your-business-website-west-hollywood-heights
5-signs-it-s-time-to-redesign-your-business-website-beverly-hills-heights
5-signs-it-s-time-to-redesign-your-business-website-north-beverly-hills
5-signs-it-s-time-to-redesign-your-business-website-beverly-hills-village
5-signs-it-s-time-to-redesign-your-business-website-glendale-heights
5-signs-it-s-time-to-redesign-your-business-website-downtown-glendale
5-signs-it-s-time-to-redesign-your-business-website-north-universal-city
5-signs-it-s-time-to-redesign-your-business-website-universal-city-heights
5-signs-it-s-time-to-redesign-your-business-website-pasadena-heights
5-signs-it-s-time-to-redesign-your-business-website-universal-city-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-pasadena
5-signs-it-s-time-to-redesign-your-business-website-pasadena-village
5-signs-it-s-time-to-redesign-your-business-website-north-san-marino
5-signs-it-s-time-to-redesign-your-business-website-san-marino-village
5-signs-it-s-time-to-redesign-your-business-website-rosemead-heights
5-signs-it-s-time-to-redesign-your-business-website-downtown-rosemead
5-signs-it-s-time-to-redesign-your-business-website-north-rosemead
5-signs-it-s-time-to-redesign-your-business-website-lynwood-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-lynwood
5-signs-it-s-time-to-redesign-your-business-website-north-lynwood
5-signs-it-s-time-to-redesign-your-business-website-north-inglewood
5-signs-it-s-time-to-redesign-your-business-website-downtown-inglewood
5-signs-it-s-time-to-redesign-your-business-website-inglewood-heights
5-signs-it-s-time-to-redesign-your-business-website-compton
5-signs-it-s-time-to-redesign-your-business-website-gardena
5-signs-it-s-time-to-redesign-your-business-website-downtown-culver-city
5-signs-it-s-time-to-redesign-your-business-website-culver-city-heights
5-signs-it-s-time-to-redesign-your-business-website-marina-del-rey
5-signs-it-s-time-to-redesign-your-business-website-venice
5-signs-it-s-time-to-redesign-your-business-website-downtown-burbank
5-signs-it-s-time-to-redesign-your-business-website-burbank-heights
5-signs-it-s-time-to-redesign-your-business-website-north-burbank
5-signs-it-s-time-to-redesign-your-business-website-burbank-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-pico-rivera
5-signs-it-s-time-to-redesign-your-business-website-north-pico-rivera
5-signs-it-s-time-to-redesign-your-business-website-pico-rivera-heights
5-signs-it-s-time-to-redesign-your-business-website-pico-rivera-village
5-signs-it-s-time-to-redesign-your-business-website-whittier
5-signs-it-s-time-to-redesign-your-business-website-south-el-monte
5-signs-it-s-time-to-redesign-your-business-website-north-san-gabriel
5-signs-it-s-time-to-redesign-your-business-website-downtown-san-gabriel
5-signs-it-s-time-to-redesign-your-business-website-arcadia
5-signs-it-s-time-to-redesign-your-business-website-temple-city
5-signs-it-s-time-to-redesign-your-business-website-el-monte
5-signs-it-s-time-to-redesign-your-business-website-sierra-madre
5-signs-it-s-time-to-redesign-your-business-website-downtown-downey
5-signs-it-s-time-to-redesign-your-business-website-downey-village
5-signs-it-s-time-to-redesign-your-business-website-downey-heights
5-signs-it-s-time-to-redesign-your-business-website-santa-fe-springs
5-signs-it-s-time-to-redesign-your-business-website-paramount
5-signs-it-s-time-to-redesign-your-business-website-bellflower
5-signs-it-s-time-to-redesign-your-business-website-norwalk
5-signs-it-s-time-to-redesign-your-business-website-studio-city-heights
5-signs-it-s-time-to-redesign-your-business-website-north-studio-city
5-signs-it-s-time-to-redesign-your-business-website-studio-city-village
5-signs-it-s-time-to-redesign-your-business-website-toluca-lake-heights
5-signs-it-s-time-to-redesign-your-business-website-downtown-toluca-lake
5-signs-it-s-time-to-redesign-your-business-website-north-toluca-lake
5-signs-it-s-time-to-redesign-your-business-website-toluca-lake-village
5-signs-it-s-time-to-redesign-your-business-website-downtown-north-hollywood
5-signs-it-s-time-to-redesign-your-business-website-north-north-hollywood
5-signs-it-s-time-to-redesign-your-business-website-north-hollywood-heights
5-signs-it-s-time-to-redesign-your-business-website-valley-village
5-signs-it-s-time-to-redesign-your-business-website-north-hollywood-village
5-signs-it-s-time-to-redesign-your-business-website-sun-valley
5-signs-it-s-time-to-redesign-your-business-website-sherman-oaks
5-signs-it-s-time-to-redesign-your-business-website-downtown-verdugo-city
5-signs-it-s-time-to-redesign-your-business-website-north-verdugo-city
5-signs-it-s-time-to-redesign-your-business-website-verdugo-city-heights
5-signs-it-s-time-to-redesign-your-business-website-montrose
5-signs-it-s-time-to-redesign-your-business-website-la-crescenta
5-signs-it-s-time-to-redesign-your-business-website-la-canada-flintridge
5-signs-it-s-time-to-redesign-your-business-website-tujunga
5-signs-it-s-time-to-redesign-your-business-website-sunland
5-signs-it-s-time-to-redesign-your-business-website-north-maywood
5-signs-it-s-time-to-redesign-your-business-website-maywood-heights
5-signs-it-s-time-to-redesign-your-business-website-maywood
5-signs-it-s-time-to-redesign-your-business-website-downtown-maywood
5-signs-it-s-time-to-redesign-your-business-website-huntington-park
5-signs-it-s-time-to-redesign-your-business-website-los-angeles
5-signs-it-s-time-to-redesign-your-business-website-bell-gardens
5-signs-it-s-time-to-redesign-your-business-website-monterey-park
5-signs-it-s-time-to-redesign-your-business-website-south-pasadena
5-signs-it-s-time-to-redesign-your-business-website-south-gate
5-signs-it-s-time-to-redesign-your-business-website-alhambra
5-signs-it-s-time-to-redesign-your-business-website-montebello
5-signs-it-s-time-to-redesign-your-business-website-west-hollywood
5-signs-it-s-time-to-redesign-your-business-website-beverly-hills
5-signs-it-s-time-to-redesign-your-business-website-universal-city
5-signs-it-s-time-to-redesign-your-business-website-glendale
5-signs-it-s-time-to-redesign-your-business-website-pasadena
5-signs-it-s-time-to-redesign-your-business-website-san-marino
5-signs-it-s-time-to-redesign-your-business-website-rosemead
5-signs-it-s-time-to-redesign-your-business-website-inglewood
5-signs-it-s-time-to-redesign-your-business-website-culver-city
5-signs-it-s-time-to-redesign-your-business-website-burbank
5-signs-it-s-time-to-redesign-your-business-website-pico-rivera
5-signs-it-s-time-to-redesign-your-business-website-san-gabriel
5-signs-it-s-time-to-redesign-your-business-website-downey
5-signs-it-s-time-to-redesign-your-business-website-studio-city
5-signs-it-s-time-to-redesign-your-business-website-toluca-lake
5-signs-it-s-time-to-redesign-your-business-website-verdugo-city
""".split()

PREFIXES = [
    "why-every-window-tinting-business-needs-a-professional-website-",
    "professional-website-designer-window-tinting-businesses-in-",
    "professional-website-designer-window-tinting-business-in-",
    "website-designer-for-window-tinting-businesses-in-",
    "website-designer-window-tinting-businesses-in-",
    "new-business-website-design-",
    "website-designing-in-",
    "wordpress-website-maintenance-downtown-in-",
    "wordpress-website-maintenance-downtown-",
    "wordpress-website-maintenance-in-",
    "wordpress-website-maintenance-",
    "5-signs-it-s-time-to-redesign-your-business-website-",
]


def place_of(slug: str) -> str:
    rest = slug
    for p in PREFIXES:
        if rest.startswith(p):
            rest = rest[len(p):]
            break
    name = rest.replace("-", " ").strip()
    special = {
        "la costa": "La Costa",
        "la mesa": "La Mesa",
        "la crescenta": "La Crescenta",
        "la canada flintridge": "La Cañada Flintridge",
        "el monte": "El Monte",
        "el cajon": "El Cajon",
        "south el monte": "South El Monte",
    }
    return special.get(name, " ".join(w.capitalize() for w in name.split()))


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


def pack(hero, mid, foot, alt_h, alt_m, alt_f):
    return hero, foot, [
        img(hero, alt_h, True),
        img(mid, alt_m, False),
        img(foot, alt_f, False),
    ]


def copy_tint(place, i):
    h1 = f"Website Design for Window Tinting Businesses in {place}"
    h2s = [
        f"What a {place} tint shop should show online",
        "Photos, services, and a clear way to book",
        f"How ZeOrbit designs the site for a {place} tint business",
    ]
    angles = [
        "auto tint, home film, and commercial glass are separate services and should not share one vague page",
        "drivers compare shops on their phone before they call, so the work photos have to load first",
        "a quote form should ask for the vehicle type instead of a blank message box",
    ]
    angle = angles[i % len(angles)]
    intro = (
        f"A window tinting shop in {place} needs a website that shows the film, the vehicles, and how to request a quote. "
        f"A generic business template does not explain ceramic tint, home window film, or how long an install takes.\n\n"
        f"This page is about website design for window tinting businesses in {place}."
    )
    content = (
        f"## {h2s[0]}\n\n"
        f"People searching in {place} want to see tinted glass, not a stock photo of a laptop. "
        f"The homepage should name auto tint, residential film, and commercial work if you offer them. "
        f"In {place}, {angle}.\n\n"
        f"## {h2s[1]}\n\n"
        f"Each service needs its own short section: what the film does, what the customer brings, and how to ask for a price. "
        f"A phone button and a short form belong on the first screen. "
        f"Before-and-after photos of real installs matter more than a long essay about design.\n\n"
        f"## {h2s[2]}\n\n"
        f"ZeOrbit builds the site around the tint shop, with pages for the services you actually sell in {place}. "
        f"We keep the layout fast on a phone, put the call button where drivers can tap it, and structure the pages so the shop can be found for window tinting in {place}.\n\n"
        f"Call ZeOrbit at (619) 724-9517 or visit [zeorbit.com](https://www.zeorbit.com/) to plan the site."
    )
    faqs = [
        {"question": f"Can ZeOrbit design a website for a tint shop in {place}?", "answer": f"Yes. The site is written for window tinting in {place}, with service pages, photos, and a way to request a quote."},
        {"question": "Should auto tint and home window film be on the same page?", "answer": "They can share a homepage, but each service should have its own section so a driver and a homeowner are not reading the same paragraph."},
        {"question": "Will the site work on a phone?", "answer": "Yes. Most tint quotes start on a phone, so the call button, photos, and form are built for a small screen first."},
        {"question": "How do I start?", "answer": "Call (619) 724-9517 or visit www.zeorbit.com with the services you want listed."},
    ]
    return h1, h1, h2s, intro, content, faqs, "Window tinting", f"website design for window tinting businesses in {place}"


def copy_new(place, i):
    h1 = f"New Business Website Design in {place}"
    h2s = [
        f"What a new {place} business site needs on day one",
        "Services, proof, and a way to reach you",
        f"How ZeOrbit launches the {place} site",
    ]
    notes = [
        "a new shop still needs a page that says what you sell before you ask for the sale",
        "neighbors will search the business name, so the site has to match that name exactly",
        "the first version should cover services, hours, and contact, then grow after you open",
    ]
    intro = (
        f"A new business in {place} should not wait for a finished brochure before it has a website. "
        f"Customers look up the name, the service, and a way to call. If that page is missing, they call the next business.\n\n"
        f"This page covers new business website design in {place}. {notes[i % 3].capitalize()}."
    )
    content = (
        f"## {h2s[0]}\n\n"
        f"The first site for a {place} business should state the offer, the area you serve, and how to get in touch. "
        f"It does not need a dozen empty pages. It needs one clear homepage and a contact path that works on a phone.\n\n"
        f"## {h2s[1]}\n\n"
        f"List the services in plain language. Add a short note about who the work is for in {place}. "
        f"Put the phone number in the header. If you have photos of the work, use those. If you do not yet, use a simple layout and add photos after you open.\n\n"
        f"## {h2s[2]}\n\n"
        f"ZeOrbit designs and builds that first site, then connects the domain, the contact form, and the pages you will add later. "
        f"The result is a {place} business website you can send to customers on opening week.\n\n"
        f"Call ZeOrbit at (619) 724-9517 or visit [zeorbit.com](https://www.zeorbit.com/)."
    )
    faqs = [
        {"question": f"Can you design a website before my {place} business opens?", "answer": "Yes. We can launch a clear services and contact site so the business has a page on day one."},
        {"question": "What pages should a new business start with?", "answer": f"A homepage, a services section, and a contact path for {place}. Extra pages can wait until you know what customers ask."},
        {"question": "Do you only use templates?", "answer": "No. The layout follows your services and your location, not a generic starter theme with the name swapped."},
        {"question": "How do I start?", "answer": "Call (619) 724-9517 or visit www.zeorbit.com and tell us the business name and what you sell."},
    ]
    return h1, h1, h2s, intro, content, faqs, "New businesses", f"new business website design in {place}"


def copy_wp(place, i):
    h1 = f"WordPress Website Maintenance in {place}"
    h2s = [
        f"What WordPress maintenance covers for a {place} site",
        "Updates, backups, and broken pages",
        f"How ZeOrbit maintains a {place} WordPress site",
    ]
    notes = [
        "a plugin update can take the contact form offline if nobody is watching",
        "spam and outdated themes are the usual reason a local site slows down",
        "backups matter before any theme or plugin change",
    ]
    intro = (
        f"A WordPress site for a business in {place} needs updates, backups, and someone to fix the page when a form or menu breaks. "
        f"Maintenance is that ongoing work, not a new design every month.\n\n"
        f"In {place}, {notes[i % 3]}."
    )
    content = (
        f"## {h2s[0]}\n\n"
        f"Maintenance means the {place} site stays online, the software stays current, and the pages customers use still work. "
        f"That includes WordPress core, plugins, the theme, and a check that the contact form sends mail.\n\n"
        f"## {h2s[1]}\n\n"
        f"We update on a schedule, keep a backup before the change, and look at speed and security notices. "
        f"If a page in the {place} menu fails after an update, that fix is part of maintenance, not a surprise rebuild.\n\n"
        f"## {h2s[2]}\n\n"
        f"ZeOrbit maintains WordPress sites for businesses that already have a site and need it looked after. "
        f"We start by checking the current theme, plugins, and backup setup for the {place} site, then agree what gets updated and how often.\n\n"
        f"Call ZeOrbit at (619) 724-9517 or visit [zeorbit.com](https://www.zeorbit.com/)."
    )
    faqs = [
        {"question": f"Do you maintain existing WordPress sites in {place}?", "answer": "Yes. We update, back up, and fix the site you already have."},
        {"question": "Is maintenance the same as a redesign?", "answer": "No. Maintenance keeps the current site working. A redesign changes the layout and the pages."},
        {"question": "What if a plugin update breaks a page?", "answer": "We restore from the backup taken before the update, then apply a safer fix."},
        {"question": "How do I start?", "answer": "Call (619) 724-9517 or visit www.zeorbit.com and share the site address."},
    ]
    return h1, h1, h2s, intro, content, faqs, "WordPress", f"WordPress website maintenance in {place}"


def copy_redesign(place, i):
    signs = [
        "the site is hard to use on a phone",
        "the services you sell now are not on the homepage",
        "the contact button is buried or the form fails",
        "the design looks like it was built years ago and customers say so",
        "you have added offers that the menu never mentions",
    ]
    h1 = f"5 Signs It's Time to Redesign Your Business Website in {place}"
    h2s = [
        f"Signs the {place} site is costing you calls",
        "What a redesign should change",
        f"How ZeOrbit redesigns a {place} business site",
    ]
    intro = (
        f"A business website in {place} needs a redesign when customers cannot tell what you do, or they cannot call you from their phone. "
        f"A new color palette is not the test. The test is whether the page helps someone in {place} choose you.\n\n"
        f"One common sign in {place}: {signs[i % 5]}."
    )
    content = (
        f"## {h2s[0]}\n\n"
        f"Look for five problems. The site is slow or broken on a phone. The services are outdated. "
        f"There is no obvious way to call or send a message. The photos do not show the work. "
        f"People in {place} land on the page and leave because the next step is unclear.\n\n"
        f"## {h2s[1]}\n\n"
        f"A redesign should rewrite the offer, rebuild the layout for a phone, and put the contact path on the first screen. "
        f"Keep the pages that already bring customers. Replace the sections that talk about services you no longer sell in {place}.\n\n"
        f"## {h2s[2]}\n\n"
        f"ZeOrbit reviews the current {place} site, lists what is failing, and rebuilds the pages around the services you want found. "
        f"The new site keeps your domain and gives customers a clearer way to reach you.\n\n"
        f"Call ZeOrbit at (619) 724-9517 or visit [zeorbit.com](https://www.zeorbit.com/)."
    )
    faqs = [
        {"question": f"When should a {place} business redesign its website?", "answer": "When the phone layout, the services, or the contact path no longer match how customers try to reach you."},
        {"question": "Do I have to throw away the current site?", "answer": "No. We keep what still works, including the domain, and replace the parts that confuse visitors."},
        {"question": "Is a redesign the same as maintenance?", "answer": "No. Maintenance updates the site you have. A redesign changes the structure and the design."},
        {"question": "How do I start?", "answer": "Call (619) 724-9517 or visit www.zeorbit.com and send the current site address."},
    ]
    return h1, h1, h2s, intro, content, faqs, "Business websites", f"website redesign in {place}"


def apply(block, slug, place, built, hero, mid, foot, alt_h, alt_m, alt_f):
    h1, title, h2s, intro, content, faqs, industry, focus = built
    meta = f"{h1}. ZeOrbit, San Diego. Call (619) 724-9517."
    featured, footer, images = pack(hero, mid, foot, alt_h, alt_m, alt_f)
    block.update({
        "slug": slug,
        "city": place,
        "title": title[:70],
        "meta_description": meta[:160],
        "h1": h1,
        "h2s": h2s,
        "h3s": h2s[:3],
        "intro": intro,
        "content": content,
        "faqs": faqs,
        "cta": f"Call ZeOrbit at (619) 724-9517 about your site in {place}.",
        "industry": industry,
        "business_type": focus,
        "focus_keyword": focus,
        "featured_image_url": featured,
        "footer_image_url": footer,
        "in_content_images": images,
        "keywords": {
            "primary": focus.lower(),
            "secondary": [industry.lower(), place.lower()],
            "long_tail": [focus.lower()],
            "near_me": [f"{industry.lower()} {place.lower()}"],
            "user_questions": [f["question"] for f in faqs],
        },
    })


def assign(pool_a, pool_b, i):
    hero = U.format(pool_a[i % len(pool_a)])
    mid = U.format(pool_b[i % len(pool_b)])
    foot = U.format(pool_a[(i + 5) % len(pool_a)])
    if foot == hero:
        foot = U.format(pool_a[(i + 6) % len(pool_a)])
    return hero, mid, foot


async def main():
    jobs = []
    for i, slug in enumerate(TINT_SLUGS):
        jobs.append((slug, "tint", i))
    for i, slug in enumerate(NEW_SLUGS):
        jobs.append((slug, "new", i))
    for i, slug in enumerate(WP_SLUGS):
        jobs.append((slug, "wp", i))
    for i, slug in enumerate(REDESIGN_SLUGS):
        jobs.append((slug, "redesign", i))

    updated, missing = [], []
    async with AsyncSessionLocal() as session:
        for slug, kind, i in jobs:
            row = (await session.execute(select(PageRecord).where(PageRecord.slug == slug))).scalar_one_or_none()
            if not row:
                missing.append(slug)
                continue
            place = place_of(slug)
            if kind == "tint":
                hero, mid, foot = assign(TINT, WEB, i)
                built = copy_tint(place, i)
                alts = (
                    f"Window tint on a car for a {place} tint shop website",
                    f"Website design layout for a {place} window tinting business",
                    f"Another tinted vehicle photo for the {place} tint shop page",
                )
            elif kind == "new":
                hero, mid, foot = assign(WEB, WEB[3:] + WEB[:3], i)
                built = copy_new(place, i)
                alts = (
                    f"New business website design workspace for {place}",
                    f"Team planning a {place} business website",
                    f"Desktop layout for a new {place} business site",
                )
            elif kind == "wp":
                hero, mid, foot = assign(CODE, CODE[4:] + CODE[:4], i)
                built = copy_wp(place, i)
                alts = (
                    f"WordPress maintenance on a laptop for a {place} business",
                    f"Code and updates for a {place} WordPress site",
                    f"Developer maintaining a WordPress site for {place}",
                )
            else:
                hero, mid, foot = assign(WEB, WEB[2:] + WEB[:2], i + 3)
                built = copy_redesign(place, i)
                alts = (
                    f"Business website redesign on a screen for {place}",
                    f"Designer rebuilding a {place} business website",
                    f"Updated website layout for a {place} company",
                )
            block = dict(row.seo_block or {})
            apply(block, slug, place, built, hero, mid, foot, *alts)
            row.seo_block = block
            flag_modified(row, "seo_block")
            updated.append(slug)
        await session.commit()
    print("updated", len(updated), "missing", len(missing))
    for s in missing:
        print(" MISSING", s)


if __name__ == "__main__":
    asyncio.run(main())
