export const SITE_CONTACT = {
  email: 'info@zeorbit.com',
  phone: '619-724-9517',
  phoneTel: '+16197249517',
  address: {
    line1: '4231 Balboa Avenue, Suite 1340',
    line2: 'San Diego, CA 92117',
  },
  offices: [
    { label: 'El Cajon', lines: ['1860 Greenfield Dr', 'El Cajon, CA 92021, USA'] },
    { label: 'Los Angeles', lines: ['3938 Red Maple Drive', 'Los Angeles, CA 90071'] },
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

/** Match zeorbit.com primary navigation (+ Blog for SEO Tool posts) */
export const PRIMARY_NAV = [
  { label: 'Home', href: '/' },
  { label: 'Website Designing', href: '/website-designing' },
  { label: 'Mobile Apps', href: '/mobile-apps' },
  { label: 'Custom Software', href: '/custom-software' },
  { label: 'SEO & PPC Tactics', href: '/seo-ppc' },
  { label: 'Blog', href: '/blog' },
  { label: 'Contact', href: '/contact' },
]

/** Why ZeOrbit — partnership themes, not a services rehash */
export const TRUST_ITEMS = [
  {
    title: 'AI-First Development',
    copy: 'Agents, automation, and model integrations designed into the product—not bolted on after launch.',
  },
  {
    title: 'Custom-Built Solutions',
    copy: 'Software, web, and mobile systems shaped around your workflows instead of forced into rigid templates.',
  },
  {
    title: 'Search & AI Visibility',
    copy: 'SEO, AEO, and GEO so your business stays discoverable in Google and AI-powered answers.',
  },
  {
    title: 'Long-Term Technology Support',
    copy: 'One U.S.-based partner from first release through iteration, growth, and ongoing engineering care.',
  },
]

/** Capability labels only — no invented metrics */
export const STATS = [
  { value: 'AI + Software', label: 'Core delivery focus' },
  { value: 'U.S. Market', label: 'Business buyers' },
  { value: 'SEO · AEO · GEO', label: 'Search coverage' },
  { value: 'Full Stack', label: 'Web · App · Automation' },
]

export const SERVICES = [
  {
    title: 'AI Solutions & AI Agents',
    description:
      'We build AI agents, copilots, and custom AI applications that handle real work—search, support, and operations—so your team ships more with less manual effort.',
    tags: ['AI Agents', 'RAG', 'GenAI'],
    art: 'ai',
    image: '/path-ai.jpg',
  },
  {
    title: 'Custom Software Development',
    description:
      'We engineer CRMs, dashboards, and business platforms around how you operate—so processes run in software that fits, not tools you work around.',
    tags: ['APIs', 'Cloud', 'Platforms'],
    art: 'software',
    image: '/service-software.jpg',
  },
  {
    title: 'Website Design & Development',
    description:
      'We build fast, conversion-ready websites with clean architecture for SEO and AI search—so visitors find you and take the next step.',
    tags: ['React', 'UX', 'Performance'],
    art: 'website',
    image: '/service-website.jpg',
  },
  {
    title: 'Mobile App Development',
    description:
      'We design and ship iOS and Android apps with secure backends—so customers get a product that works in the store and in daily use.',
    tags: ['iOS', 'Android', 'APIs'],
    art: 'app',
    image: '/service-app.jpg',
  },
  {
    title: 'Business Automation',
    description:
      'We connect systems and automate repeatable workflows—so operations stay reliable as volume grows without adding headcount for every task.',
    tags: ['Workflows', 'Integrations', 'Ops'],
    art: 'automation',
    image: '/path-automate.jpg',
  },
  {
    title: 'SEO / AEO / GEO',
    description:
      'We strengthen technical SEO and prepare content for answer engines and generative search—so you show up where buyers and AI systems look.',
    tags: ['Technical SEO', 'AEO', 'GEO'],
    art: 'seo',
    image: '/service-seo.jpg',
  },
  {
    title: 'Ecommerce Optimization',
    description:
      'We improve storefront speed, catalog structure, and checkout flows—so more visits turn into completed orders.',
    tags: ['Shopify', 'WooCommerce', 'CRO'],
    art: 'ecommerce',
    image: '/service-ecommerce.jpg',
  },
  {
    title: 'Data Processing & Analytics',
    description:
      'We build pipelines and reporting layers from your web and business data—so decisions rest on clear signals, not spreadsheets alone.',
    tags: ['Pipelines', 'Analytics', 'Reporting'],
    art: 'data',
    image: '/service-data.jpg',
  },
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
  { id: '01', title: 'Discover', copy: 'Clarify goals, users, systems, and constraints before any build starts.' },
  { id: '02', title: 'Strategize', copy: 'Define architecture, scope, channel plan, and success criteria up front.' },
  { id: '03', title: 'Design', copy: 'Create UX that makes the offer clear and the next action obvious.' },
  { id: '04', title: 'Engineer', copy: 'Ship secure web, mobile, software, automation, and AI integrations.' },
  { id: '05', title: 'Launch', copy: 'Release with QA, analytics, SEO baselines, and a handoff your team can run.' },
  { id: '06', title: 'Optimize', copy: 'Improve performance, search visibility, automation, and product outcomes over time.' },
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
    category: 'AI Search',
    title: 'How AEO and GEO change how U.S. buyers find service brands',
    excerpt: 'A practical view of answer engines, citations, and what your site must expose to be recommended.',
  },
  {
    category: 'Engineering',
    title: 'Why performance architecture still decides conversion',
    excerpt: 'How Core Web Vitals, accessibility, and clear UX affect lead quality—not just rankings.',
  },
  {
    category: 'Growth',
    title: 'Connecting SEO, paid media, and AI workflows into one loop',
    excerpt: 'How content, campaigns, and automation reinforce each other when data stays shared.',
  },
]

/** Interactive paths — engineering outcomes, not a fake portfolio */
export const BUILD_PATHS = [
  {
    key: 'grow',
    label: 'Grow My Business',
    eyebrow: 'Search + Conversion',
    revealTitle: 'Turn discovery into qualified demand.',
    revealBody:
      'Challenge: buyers find you in Google and AI answers, but traffic does not convert. Solution: SEO, AEO, GEO, and paid search on a site built to capture demand. Technology: technical SEO, content systems, analytics. Result: clearer pipeline from search to contact.',
    cardImage: '/path-grow.jpg',
    revealImage: '/path-reveal-grow.jpg',
    items: ['SEO', 'AEO', 'GEO', 'Paid Search', 'Content', 'Analytics'],
  },
  {
    key: 'ai',
    label: 'Build With AI',
    eyebrow: 'AI that works daily',
    revealTitle: 'Put practical AI inside how you already work.',
    revealBody:
      'Challenge: AI demos that never reach production. Solution: agents, generative AI, RAG, and workflow automation wired to your tools. Technology: ChatGPT, Claude, Gemini, and custom AI apps. Result: systems your team uses every day—not a slide deck.',
    cardImage: '/path-ai.jpg',
    revealImage: '/path-reveal-ai.jpg',
    items: ['AI Agents', 'Generative AI', 'RAG', 'Automation', 'AI Search'],
  },
  {
    key: 'website',
    label: 'Build a Website',
    eyebrow: 'Web engineering',
    revealTitle: 'Launch a site built for speed, search, and conversion.',
    revealBody:
      'Challenge: a site that looks fine but underperforms. Solution: modern web development with performance budgets and search-ready structure. Technology: responsive builds, CMS, technical SEO. Result: a foundation that supports growth and AI visibility.',
    cardImage: '/path-website.jpg',
    revealImage: '/path-reveal-website.jpg',
    items: ['Web Development', 'UX Systems', 'Performance', 'Technical SEO', 'CMS'],
  },
  {
    key: 'app',
    label: 'Create an App',
    eyebrow: 'Product engineering',
    revealTitle: 'Ship a mobile product ready for real users.',
    revealBody:
      'Challenge: an app idea without a path to the stores. Solution: iOS, Android, or cross-platform delivery with secure APIs. Technology: Flutter, React Native, cloud backends. Result: a product you can release, measure, and improve.',
    cardImage: '/path-app.jpg',
    revealImage: '/path-reveal-app.jpg',
    items: ['iOS', 'Android', 'Flutter', 'React Native', 'APIs', 'Cloud'],
  },
  {
    key: 'automate',
    label: 'Automate My Business',
    eyebrow: 'Ops + integrations',
    revealTitle: 'Replace repetitive work with reliable automation.',
    revealBody:
      'Challenge: teams stuck in manual handoffs between tools. Solution: workflow automation and API integrations with monitoring. Technology: orchestration, data pipelines, alerts. Result: operations that scale without adding friction for every new order.',
    cardImage: '/path-automate.jpg',
    revealImage: '/path-reveal-automate.jpg',
    items: ['Business Automation', 'API Integrations', 'Data Pipelines', 'Monitoring', 'AI Assist'],
  },
]
