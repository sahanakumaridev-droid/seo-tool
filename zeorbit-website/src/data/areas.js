/** Areas we serve — Tier A city pages + hub chips. */

export const AREA_HUB = {
  eyebrow: 'Areas we serve',
  title: 'San Diego based. Nationwide reach.',
  lead:
    'ZeOrbit is a U.S. digital agency headquartered in San Diego. We design websites, build apps, and run SEO & ads for brands across California and beyond.',
  metaTitle: 'Areas We Serve — ZeOrbit',
  metaDescription:
    'ZeOrbit serves San Diego, El Cajon, Los Angeles, Orange County, and clients nationwide with websites, apps, SEO, and custom software.',
}

/** Live Tier A pages (v1). */
export const AREA_PAGES = {
  'san-diego': {
    slug: 'san-diego',
    name: 'San Diego',
    label: 'San Diego, CA',
    region: 'California',
    eyebrow: 'San Diego HQ',
    title: 'Websites, apps & growth for San Diego brands',
    lead:
      'From Clairemont Mesa to the county’s fastest-growing businesses, we help San Diego companies launch sharper digital products — and keep them converting.',
    why: [
      'San Diego is our home base — local meetings when you want them, remote velocity when you don’t.',
      'We know the local competitive landscape: tourism, healthcare, biotech, restaurants, and service brands fighting for the same Google real estate.',
      'Our San Diego HQ keeps strategy, design, and engineering in one loop so projects don’t stall between vendors.',
    ],
    services: [
      { label: 'Website design', to: '/website-designing' },
      { label: 'Mobile apps', to: '/mobile-apps' },
      { label: 'SEO & ads', to: '/seo-ppc' },
      { label: 'Custom software', to: '/custom-software' },
    ],
    faqs: [
      {
        q: 'Do you meet clients in San Diego?',
        a: 'Yes. We’re based in San Diego and can meet in person for discovery, reviews, and kickoffs when it helps the project.',
      },
      {
        q: 'Can you help with local SEO in San Diego?',
        a: 'Yes — Google Business Profile, location pages, maps visibility, and content that ranks for the searches your customers actually type.',
      },
    ],
    metaTitle: 'San Diego Web Design & Digital Agency — ZeOrbit',
    metaDescription:
      'ZeOrbit is a San Diego digital agency for websites, mobile apps, SEO, and custom software. Get a free quote from our local HQ.',
  },
  'el-cajon': {
    slug: 'el-cajon',
    name: 'El Cajon',
    label: 'El Cajon, CA',
    region: 'East County, San Diego',
    eyebrow: 'East County studio',
    title: 'Digital products for El Cajon & East County',
    lead:
      'We support El Cajon and East County businesses that need a modern website, a reliable app, or stronger local search — without agency fluff.',
    why: [
      'East County brands often compete against bigger San Diego players online — we build sites and campaigns that punch above that weight.',
      'Clear scopes, honest timelines, and delivery you can show stakeholders.',
      'Close enough for local collaboration, structured enough for nationwide standards.',
    ],
    services: [
      { label: 'Website redesign', to: '/website-designing#redesign' },
      { label: 'Local SEO', to: '/seo-ppc#local' },
      { label: 'Landing pages', to: '/website-designing#landing' },
      { label: 'Care & maintenance', to: '/website-designing#care' },
    ],
    faqs: [
      {
        q: 'Do you work with small El Cajon businesses?',
        a: 'Absolutely. Many of our best projects start with local owners who need a clean site, better leads, and a partner who explains options plainly.',
      },
      {
        q: 'How fast can we launch?',
        a: 'Depends on scope — a focused landing page can move quickly; a full redesign or app needs a proper discovery pass. We’ll map a realistic timeline on the first call.',
      },
    ],
    metaTitle: 'El Cajon Web Design & SEO — ZeOrbit',
    metaDescription:
      'ZeOrbit builds websites, SEO, and digital products for El Cajon and East County businesses. Talk to our San Diego–area team.',
  },
  'los-angeles': {
    slug: 'los-angeles',
    name: 'Los Angeles',
    label: 'Los Angeles, CA',
    region: 'Southern California',
    eyebrow: 'Los Angeles',
    title: 'Agency-grade digital for Los Angeles brands',
    lead:
      'We partner with LA companies that want conversion-focused websites, store-ready apps, and growth systems — delivered with San Diego craft and LA pace.',
    why: [
      'LA markets move fast and look crowded. We prioritize clarity, speed, and conversion over decorative redesigns.',
      'Remote-first collaboration with optional onsite sessions for kickoffs and reviews.',
      'One team for design, build, and post-launch SEO/ads so handoffs don’t kill momentum.',
    ],
    services: [
      { label: 'Custom websites', to: '/website-designing#business' },
      { label: 'Shopify & ecommerce', to: '/website-designing#ecommerce' },
      { label: 'iOS & Android apps', to: '/mobile-apps#native' },
      { label: 'Google Ads', to: '/seo-ppc#ads' },
    ],
    faqs: [
      {
        q: 'Are you an LA agency?',
        a: 'We’re San Diego–based and serve Los Angeles clients nationwide-style: async by default, meetings when they matter, and production that doesn’t depend on a downtown office.',
      },
      {
        q: 'Can you support multi-location LA brands?',
        a: 'Yes — shared design systems, location pages, and local SEO structures that keep each market distinct without duplicating junk content.',
      },
    ],
    metaTitle: 'Los Angeles Web Design & Apps — ZeOrbit',
    metaDescription:
      'ZeOrbit builds websites, apps, and growth campaigns for Los Angeles brands. Get a free quote from our U.S. digital agency.',
  },
  'orange-county': {
    slug: 'orange-county',
    name: 'Orange County',
    label: 'Orange County',
    region: 'Southern California',
    eyebrow: 'Orange County',
    title: 'Websites & growth for Orange County businesses',
    lead:
      'From Irvine to the coast, we help OC brands ship polished digital experiences that turn visitors into customers.',
    why: [
      'OC companies often need premium polish and measurable leads — we design for both.',
      'Tight collaboration across website, SEO, and ads so creative and performance stay aligned.',
      'Built for founders and marketing leads who want clear ownership, not endless status theater.',
    ],
    services: [
      { label: 'UI / UX design', to: '/website-designing#ux' },
      { label: 'Technical SEO', to: '/seo-ppc#seo' },
      { label: 'Content SEO', to: '/seo-ppc#content' },
      { label: 'Custom software', to: '/custom-software' },
    ],
    faqs: [
      {
        q: 'Do you serve all of Orange County?',
        a: 'Yes — Irvine, Anaheim, Newport, Costa Mesa, and surrounding OC markets. Most work is remote with scheduled video reviews.',
      },
      {
        q: 'What industries do you work with in OC?',
        a: 'Professional services, ecommerce, healthcare-adjacent, hospitality, and product companies — anywhere a sharper site and clearer funnel matter.',
      },
    ],
    metaTitle: 'Orange County Web Design & SEO — ZeOrbit',
    metaDescription:
      'ZeOrbit helps Orange County businesses with website design, SEO, apps, and custom software. Request a free project quote.',
    tier: 'a',
  },
  california: {
    slug: 'california',
    name: 'California',
    label: 'California',
    region: 'West Coast',
    eyebrow: 'California',
    title: 'Digital agency for California brands',
    lead:
      'From San Diego to the Bay Area, we help California companies ship websites, apps, and growth systems that hold up in competitive markets.',
    why: [
      'California audiences expect fast, polished experiences — we design for conversion and clarity, not decoration.',
      'Statewide collaboration with a San Diego HQ for strategy and delivery.',
      'One partner across website, SEO, ads, and software so campaigns and product stay aligned.',
    ],
    services: [
      { label: 'Website design', to: '/website-designing' },
      { label: 'SEO & ads', to: '/seo-ppc' },
      { label: 'Mobile apps', to: '/mobile-apps' },
      { label: 'Custom software', to: '/custom-software' },
    ],
    faqs: [
      {
        q: 'Do you only work in Southern California?',
        a: 'No. We’re based in San Diego and serve clients across California — LA, OC, the Central Valley, and Northern California — mostly remote with video reviews.',
      },
      {
        q: 'Can you support multi-city California brands?',
        a: 'Yes. We build shared design systems and location-aware SEO structures so each market stays distinct without thin duplicate pages.',
      },
    ],
    metaTitle: 'California Web Design & Digital Agency — ZeOrbit',
    metaDescription:
      'ZeOrbit serves California brands with websites, apps, SEO, and custom software. Get a free quote from our San Diego HQ.',
    tier: 'b',
  },
  texas: {
    slug: 'texas',
    name: 'Texas',
    label: 'Texas',
    region: 'South Central',
    eyebrow: 'Texas',
    title: 'Websites & growth for Texas businesses',
    lead:
      'We partner with Texas brands that need a sharper website, stronger local/national search, or a custom digital product — delivered remotely with U.S. agency standards.',
    why: [
      'Texas markets are competitive and scale fast — we prioritize speed-to-clarity and measurable leads.',
      'Async-first process that works across time zones without losing craft.',
      'Full-stack delivery: design, build, SEO, and ads in one team.',
    ],
    services: [
      { label: 'Custom websites', to: '/website-designing#business' },
      { label: 'Local SEO', to: '/seo-ppc#local' },
      { label: 'Google Ads', to: '/seo-ppc#ads' },
      { label: 'Landing pages', to: '/website-designing#landing' },
    ],
    faqs: [
      {
        q: 'Do you have a Texas office?',
        a: 'We’re San Diego–based and serve Texas clients remotely. Kickoffs and reviews happen on video; travel can be arranged for larger engagements.',
      },
      {
        q: 'What Texas cities do you work with?',
        a: 'Austin, Dallas, Houston, San Antonio, and growing metros statewide — wherever a clearer funnel and stronger site matter.',
      },
    ],
    metaTitle: 'Texas Web Design & SEO — ZeOrbit',
    metaDescription:
      'ZeOrbit builds websites, SEO, and digital products for Texas businesses. Request a free project quote.',
    tier: 'b',
  },
  florida: {
    slug: 'florida',
    name: 'Florida',
    label: 'Florida',
    region: 'Southeast',
    eyebrow: 'Florida',
    title: 'Digital products for Florida brands',
    lead:
      'We help Florida companies launch conversion-focused websites and growth campaigns that stand out in tourism, services, and ecommerce markets.',
    why: [
      'Florida competitors often look the same online — we push clear positioning and faster paths to inquiry.',
      'Remote delivery with structured milestones and transparent communication.',
      'SEO and paid media options when you’re ready to scale traffic after launch.',
    ],
    services: [
      { label: 'Website redesign', to: '/website-designing#redesign' },
      { label: 'SEO & content', to: '/seo-ppc#content' },
      { label: 'Ecommerce', to: '/website-designing#ecommerce' },
      { label: 'Care & maintenance', to: '/website-designing#care' },
    ],
    faqs: [
      {
        q: 'Can you work with hospitality and tourism brands in Florida?',
        a: 'Yes — booking paths, mobile performance, and local search matter a lot in those verticals, and we design for them.',
      },
      {
        q: 'How do projects run remotely?',
        a: 'Discovery call, shared timeline, design reviews on video, and async updates between milestones so you always know what’s next.',
      },
    ],
    metaTitle: 'Florida Web Design & Digital Agency — ZeOrbit',
    metaDescription:
      'ZeOrbit serves Florida businesses with website design, SEO, apps, and custom software. Get a free quote today.',
    tier: 'b',
  },
  'new-york': {
    slug: 'new-york',
    name: 'New York',
    label: 'New York',
    region: 'Northeast',
    eyebrow: 'New York',
    title: 'Agency craft for New York brands',
    lead:
      'We work with New York companies that want polished digital experiences and growth systems — without the overhead of a bloated agency roster.',
    why: [
      'NY markets move quickly; we keep scopes tight and delivery accountable.',
      'Design and engineering in one loop so handoffs don’t slow launches.',
      'Optional SEO/ads after launch when traffic needs to match the new experience.',
    ],
    services: [
      { label: 'UI / UX design', to: '/website-designing#ux' },
      { label: 'Custom websites', to: '/website-designing#business' },
      { label: 'Mobile apps', to: '/mobile-apps' },
      { label: 'Technical SEO', to: '/seo-ppc#seo' },
    ],
    faqs: [
      {
        q: 'Do you work with NYC startups and established brands?',
        a: 'Both. We adapt process to your stage — lean MVP sites for early teams, fuller systems for brands that need governance and scale.',
      },
      {
        q: 'What are typical meeting times?',
        a: 'We schedule around Eastern hours when needed. Most collaboration is async with planned review calls.',
      },
    ],
    metaTitle: 'New York Web Design & Apps — ZeOrbit',
    metaDescription:
      'ZeOrbit builds websites, apps, and SEO for New York brands. Talk to our U.S. digital agency for a free quote.',
    tier: 'b',
  },
  arizona: {
    slug: 'arizona',
    name: 'Arizona',
    label: 'Arizona',
    region: 'Southwest',
    eyebrow: 'Arizona',
    title: 'Websites & SEO for Arizona businesses',
    lead:
      'We help Arizona brands modernize their digital presence — clearer websites, stronger local visibility, and practical growth campaigns.',
    why: [
      'Phoenix and surrounding markets are competitive for local services — we build for search and conversion together.',
      'Straightforward scopes and honest timelines.',
      'San Diego–based team with nationwide remote delivery.',
    ],
    services: [
      { label: 'Local SEO', to: '/seo-ppc#local' },
      { label: 'Landing pages', to: '/website-designing#landing' },
      { label: 'Website design', to: '/website-designing' },
      { label: 'Google Ads', to: '/seo-ppc#ads' },
    ],
    faqs: [
      {
        q: 'Do you serve Phoenix and Tucson?',
        a: 'Yes — and other Arizona metros. Most work is remote with video discovery and reviews.',
      },
      {
        q: 'Can you improve Google Business Profile visibility?',
        a: 'Yes. Local SEO packages can include GBP optimization, location content, and tracking so you see what converts.',
      },
    ],
    metaTitle: 'Arizona Web Design & Local SEO — ZeOrbit',
    metaDescription:
      'ZeOrbit helps Arizona businesses with website design, local SEO, and digital growth. Request a free quote.',
    tier: 'b',
  },
  nationwide: {
    slug: 'nationwide',
    name: 'Nationwide U.S.',
    label: 'Nationwide U.S.',
    region: 'United States',
    eyebrow: 'Nationwide',
    title: 'A U.S. digital agency for brands everywhere',
    lead:
      'ZeOrbit is San Diego–based and serves clients across the United States — websites, apps, SEO, and custom software with one accountable team.',
    why: [
      'Remote-first delivery that still feels hands-on: clear owners, milestones, and demos.',
      'National standards with local market awareness when SEO or ads need geo focus.',
      'One stack for design, engineering, and growth — fewer vendors, fewer gaps.',
    ],
    services: [
      { label: 'Website design', to: '/website-designing' },
      { label: 'Mobile apps', to: '/mobile-apps' },
      { label: 'SEO & ads', to: '/seo-ppc' },
      { label: 'Custom software', to: '/custom-software' },
    ],
    faqs: [
      {
        q: 'Do you only work with California clients?',
        a: 'No. California is home base; we regularly work with teams across the U.S. via video and async collaboration.',
      },
      {
        q: 'How do we start?',
        a: 'Send a short brief through our contact form. We’ll reply with fit, next steps, and a realistic timeline.',
      },
    ],
    metaTitle: 'Nationwide U.S. Digital Agency — ZeOrbit',
    metaDescription:
      'ZeOrbit is a U.S. digital agency for websites, apps, SEO, and software — serving brands nationwide from San Diego.',
    tier: 'b',
  },
}

export const AREA_SLUGS = Object.keys(AREA_PAGES)

export const AREA_TIER_A = AREA_SLUGS.filter((slug) => AREA_PAGES[slug].tier !== 'b')
export const AREA_TIER_B = AREA_SLUGS.filter((slug) => AREA_PAGES[slug].tier === 'b')

/** Chips on Contact — every item has its own page. */
export const AREA_CHIPS = [
  { label: 'San Diego, CA', slug: 'san-diego' },
  { label: 'Los Angeles, CA', slug: 'los-angeles' },
  { label: 'El Cajon, CA', slug: 'el-cajon' },
  { label: 'Orange County', slug: 'orange-county' },
  { label: 'California', slug: 'california' },
  { label: 'Texas', slug: 'texas' },
  { label: 'Florida', slug: 'florida' },
  { label: 'New York', slug: 'new-york' },
  { label: 'Arizona', slug: 'arizona' },
  { label: 'Nationwide U.S.', slug: 'nationwide' },
]

export function getAreaPage(slug) {
  return AREA_PAGES[slug] || null
}
