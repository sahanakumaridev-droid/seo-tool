export const SITE_CONTACT = {
  email: 'info@zeorbit.com',
  phone: '619-724-9517',
  phoneTel: '+16197249517',
  address: {
    line1: '4231 Balboa Avenue, Suite 1340',
    line2: 'San Diego, CA 92117',
    mapsUrl:
      'https://www.google.com/maps/search/?api=1&query=4231+Balboa+Avenue+Suite+1340+San+Diego+CA+92117',
  },
  offices: [
    {
      label: 'El Cajon',
      lines: ['1860 Greenfield Dr', 'El Cajon, CA 92021, USA'],
      mapsUrl:
        'https://www.google.com/maps/search/?api=1&query=1860+Greenfield+Dr+El+Cajon+CA+92021',
    },
    {
      label: 'Los Angeles',
      lines: ['3938 Red Maple Drive', 'Los Angeles, CA 90071'],
      mapsUrl:
        'https://www.google.com/maps/search/?api=1&query=3938+Red+Maple+Drive+Los+Angeles+CA+90071',
    },
  ],
  social: [
    { label: 'Facebook', href: 'https://www.facebook.com/zeorbit.zeorbit' },
    { label: 'LinkedIn', href: 'https://www.linkedin.com/company/zeorbit/' },
    { label: 'Instagram', href: 'https://www.instagram.com/zeorbit/' },
    { label: 'YouTube', href: 'https://www.youtube.com/@ZeOrbit-Firm/about' },
    { label: 'X', href: 'https://twitter.com/orbit_ze' },
    { label: 'Pinterest', href: 'https://www.pinterest.com/zeorbitsd/' },
  ],
  google: {
    placeId: 'ChIJpd4HFaVZ2YARFUApQxHkD30',
    reviewsUrl: 'https://search.google.com/local/reviews?placeid=ChIJpd4HFaVZ2YARFUApQxHkD30',
    writeReviewUrl: 'https://search.google.com/local/writereview?placeid=ChIJpd4HFaVZ2YARFUApQxHkD30',
    rating: '5.0',
    reviewCount: 28,
    businessName: 'ZeOrbit - Website Designer & Mobile App Development',
  },
}

/** Primary nav — unique destinations only (no duplicate child links). */
export const PRIMARY_NAV = [
  { label: 'Home', href: '/' },
  {
    label: 'Websites',
    href: '/website-designing',
    children: [
      { label: 'Custom Websites', href: '/website-designing#business' },
      { label: 'Shopify & Ecommerce', href: '/website-designing#ecommerce' },
      { label: 'Landing Pages', href: '/website-designing#landing' },
      { label: 'Website Redesign', href: '/website-designing#redesign' },
      { label: 'UI / UX Design', href: '/website-designing#ux' },
      { label: 'Care & Maintenance', href: '/website-designing#care' },
    ],
  },
  {
    label: 'Mobile Apps',
    href: '/mobile-apps',
    children: [
      { label: 'iOS & Android', href: '/mobile-apps#native' },
      { label: 'Cross-Platform', href: '/mobile-apps#cross' },
      { label: 'App Timeline', href: '/mobile-apps#timeline' },
      { label: 'Mobile UX / UI', href: '/mobile-apps#ux' },
    ],
  },
  {
    label: 'SEO & Ads',
    href: '/seo-ppc',
    children: [
      { label: 'Technical SEO', href: '/seo-ppc#seo' },
      { label: 'Local SEO', href: '/seo-ppc#local' },
      { label: 'Content SEO', href: '/seo-ppc#content' },
      { label: 'Google Ads', href: '/seo-ppc#ads' },
      { label: 'Social Ads', href: '/seo-ppc#social-ads' },
    ],
  },
  {
    label: 'Software',
    href: '/custom-software',
    children: [
      { label: 'Dashboards', href: '/custom-software#platforms' },
      { label: 'CRM & Workflows', href: '/custom-software#crm' },
      { label: 'API Integrations', href: '/custom-software#integrations' },
      { label: 'Automation', href: '/custom-software#automation' },
    ],
  },
  { label: 'Blog', href: '/blog' },
  {
    label: 'Contact',
    href: '/contact',
    children: [{ label: 'Areas We Serve', href: '/contact#areas' }],
  },
]

export const TRUST_ITEMS = [
  {
    title: 'Website platforms that fit',
    copy: 'WordPress, Shopify, Wix, and Squarespace — built clean, fast, and ready to convert.',
  },
  {
    title: 'Apps for iOS and Android',
    copy: 'Store-ready mobile products with clear UX and solid backends.',
  },
  {
    title: 'Design that converts',
    copy: 'UX and UI focused on one job: get the visitor to take the next step.',
  },
  {
    title: 'Growth after launch',
    copy: 'SEO, GEO, PPC, and Google Ads when you are ready to scale traffic.',
  },
]

export const STATS = [
  { value: 'Websites', label: 'WordPress · Shopify · Wix · Squarespace' },
  { value: 'Mobile', label: 'iOS · Android' },
  { value: 'U.S. based', label: 'San Diego headquarters' },
  { value: 'Growth', label: 'SEO · GEO · PPC · Ads' },
]

/** Homepage pillars — website + mobile first, growth later */
export const SERVICES = [
  {
    title: 'Website Development',
    description:
      'Custom sites on WordPress, Shopify, Wix, and Squarespace — designed to look sharp and turn visitors into leads.',
    tags: ['WordPress', 'Shopify', 'Wix', 'Squarespace'],
    art: 'website',
    image: '/service-website.jpg',
    href: '/website-designing',
  },
  {
    title: 'Mobile App Development',
    description:
      'iOS and Android apps built for real users — from first screen to App Store and Google Play.',
    tags: ['iOS', 'Android'],
    art: 'app',
    image: '/service-app.jpg',
    href: '/mobile-apps',
  },
  {
    title: 'UX & UI Design',
    description:
      'Clear layouts, strong hierarchy, and interfaces that make the next action obvious.',
    tags: ['UX', 'UI', 'Prototyping'],
    art: 'website',
    image: '/path-website.jpg',
    href: '/website-designing',
  },
  {
    title: 'SEO, GEO & PPC',
    description:
      'Get found on Google and grow with search, local visibility, and paid campaigns.',
    tags: ['SEO', 'GEO', 'PPC', 'Google Ads'],
    art: 'seo',
    image: '/service-seo.jpg',
    href: '/seo-ppc',
  },
  {
    title: 'Ecommerce Stores',
    description:
      'Shopify and WooCommerce storefronts tuned for speed, catalog clarity, and checkout.',
    tags: ['Shopify', 'WooCommerce'],
    art: 'ecommerce',
    image: '/service-ecommerce.jpg',
    href: '/website-designing',
  },
  {
    title: 'Custom Software & AI',
    description:
      'Business platforms and practical AI tools — added when your website or app needs them.',
    tags: ['Software', 'Automation', 'AI'],
    art: 'software',
    image: '/service-software.jpg',
    href: '/custom-software',
  },
]

export const PLATFORM_ITEMS = [
  { name: 'WordPress', note: 'Flexible sites and blogs' },
  { name: 'Shopify', note: 'Ecommerce that sells' },
  { name: 'Wix', note: 'Fast, polished launches' },
  { name: 'Squarespace', note: 'Design-led brands' },
]

export const AI_SOLUTIONS = [
  'AI Agents',
  'Generative AI',
  'Workflow Automation',
  'RAG',
  'AI Search',
  'ChatGPT Integrations',
  'Claude Integrations',
  'Gemini Integrations',
  'Custom AI Applications',
]

export const PROCESS_STEPS = [
  { id: '01', title: 'Discover', copy: 'Goals, audience, and platform — before a single page is built.' },
  { id: '02', title: 'Design', copy: 'UX and UI that put your offer and next step front and center.' },
  { id: '03', title: 'Build', copy: 'Website or app on the right stack: WordPress, Shopify, Wix, Squarespace, iOS, or Android.' },
  { id: '04', title: 'Launch', copy: 'QA, analytics, and a clean handoff your team can run.' },
  { id: '05', title: 'Grow', copy: 'SEO, GEO, PPC, and Google Ads when you are ready for more traffic.' },
]

export const INDUSTRIES = [
  'Healthcare',
  'Legal',
  'Home Services',
  'Real Estate',
  'Ecommerce',
  'Professional Services',
]

export const INSIGHTS = [
  {
    category: 'Websites',
    title: 'Choosing WordPress, Shopify, Wix, or Squarespace',
    excerpt: 'A plain-English guide to picking the platform that fits your business — not the trend.',
  },
  {
    category: 'Mobile',
    title: 'What makes an iOS and Android app worth launching',
    excerpt: 'Scope, UX, and store readiness — without overbuilding on day one.',
  },
  {
    category: 'Growth',
    title: 'SEO, GEO, and Google Ads after your site launches',
    excerpt: 'How to get found once the website or app is live.',
  },
]

/** Interactive paths — website + mobile first */
export const BUILD_PATHS = [
  {
    key: 'website',
    label: 'Build a Website',
    eyebrow: 'Web platforms',
    revealTitle: 'A site on WordPress, Shopify, Wix, or Squarespace.',
    revealBody:
      'We design and build conversion-ready websites on the platform that fits your business — fast, clear, and ready for SEO.',
    cardImage: '/path-website.jpg',
    revealImage: '/path-reveal-website.jpg',
    items: ['WordPress', 'Shopify', 'Wix', 'Squarespace', 'UX/UI'],
  },
  {
    key: 'app',
    label: 'Create an App',
    eyebrow: 'Mobile',
    revealTitle: 'iOS and Android apps ready for real users.',
    revealBody:
      'From first screen to store listing — native or cross-platform apps with secure backends and clean UX.',
    cardImage: '/path-app.jpg',
    revealImage: '/path-reveal-app.jpg',
    items: ['iOS', 'Android', 'UX', 'APIs', 'Store launch'],
  },
  {
    key: 'grow',
    label: 'Grow Traffic',
    eyebrow: 'SEO + Ads',
    revealTitle: 'Get found with SEO, GEO, PPC, and Google Ads.',
    revealBody:
      'Once your site or app is live, we help buyers find you — organic search, local visibility, and paid campaigns.',
    cardImage: '/path-grow.jpg',
    revealImage: '/path-reveal-grow.jpg',
    items: ['SEO', 'GEO', 'PPC', 'Google Ads'],
  },
  {
    key: 'automate',
    label: 'Add Software & AI',
    eyebrow: 'When you need more',
    revealTitle: 'Custom software and practical AI on top of your stack.',
    revealBody:
      'CRMs, automation, and AI tools that plug into the website or app you already run.',
    cardImage: '/path-automate.jpg',
    revealImage: '/path-reveal-automate.jpg',
    items: ['Custom Software', 'Automation', 'AI'],
  },
]
