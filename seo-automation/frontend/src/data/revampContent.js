/** SEO landing in-page anchors (legacy/simple headers). */
export const PRIMARY_NAV = [
  { label: 'Product', href: '#features' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

/** Same contact block as zeorbit.com — used by matching header/footer chrome. */
export const SITE_CONTACT = {
  email: 'info@zeorbit.com',
  phone: '619-724-9517',
  phoneTel: '+16197249517',
  social: [
    { label: 'Facebook', href: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers' },
    { label: 'Instagram', href: 'https://www.instagram.com/zeorbit/' },
    { label: 'LinkedIn', href: 'https://www.linkedin.com/company/zeorbit/' },
    { label: 'YouTube', href: 'https://www.youtube.com/@ZeOrbit-Firm' },
    { label: 'X', href: 'https://twitter.com/orbit_ze' },
    { label: 'Pinterest', href: 'https://www.pinterest.com/zeorbitsd/' },
    { label: 'Apple Maps', href: 'https://maps.apple/p/VA-_LREgJ5PzDV' },
    { label: 'Google Maps', href: 'https://maps.app.goo.gl/teVefHUc3yycwkcA7' },
    { label: 'Yelp', href: 'https://www.yelp.com/biz/zeorbit-san-diego-2' },
  ],
}

/** Same primary nav as zeorbit.com (paths resolve under SITE_ORIGIN). */
export const SITE_PRIMARY_NAV = [
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
      { label: 'Blog & Insights', href: '/seo-ppc#blog' },
      { label: 'Pricing', href: '/seo-ppc#pricing' },
    ],
  },
  {
    label: 'Custom Software',
    href: '/custom-software',
    children: [
      { label: 'Dashboards', href: '/custom-software#platforms' },
      { label: 'CRM & Workflows', href: '/custom-software#crm' },
      { label: 'API Integrations', href: '/custom-software#integrations' },
      { label: 'Automation', href: '/custom-software#automation' },
    ],
  },
  { label: 'Work', href: '/portfolio' },
  { label: 'Contact', href: '/contact' },
]

export const SITE_ORIGIN = 'https://zeorbit.com'

export function siteUrl(path = '/') {
  if (!path) return SITE_ORIGIN
  if (/^https?:\/\//i.test(path)) return path
  return `${SITE_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`
}

export const TRUST_ITEMS = [
  'Site Performance',
  'Keyword Research',
  'AI Visibility',
  'Competitive Analysis',
  'Content',
  'Link Building',
  'Local',
  'Reports',
]

export const FEATURE_BLOCKS = [
  {
    id: 'site',
    label: 'Site Performance',
    title: 'Scan your website for 140+ SEO and AI search issues',
    bullets: [
      'See your Site Health and AI Search Health scores side by side',
      'Audit the technical elements AI engines rely on: structured data, semantic HTML, internal linking, content structure, and more',
      'Prioritize and fix issues affecting your search and AI visibility',
    ],
  },
  {
    id: 'keywords',
    label: 'Keyword Research',
    title: 'Target the best keywords with AI',
    bullets: [
      'Search any topic, competitor, or niche and uncover thousands of keyword ideas',
      'Identify high-value keywords based on search volume, difficulty, intent, and AI Overview opportunities',
      'Answer SEO questions with ZeOrbit data in ChatGPT, Claude, and other AI tools',
    ],
  },
  {
    id: 'ai',
    label: 'AI Visibility',
    title: 'Measure and grow your AI visibility',
    bullets: [
      'Track any brand’s AI Visibility Score to see how often it appears in AI responses',
      'Discover trending topics people ask AI and use them to guide your content strategy',
      'Identify prompts and sources where competitors appear and close the gap',
    ],
  },
  {
    id: 'competitors',
    label: 'Competitive Analysis',
    title: 'See the strategy behind any competitor’s growth',
    bullets: [
      'Get a full overview of a domain and its online visibility',
      'See your competitors’ best keywords, paid strategy, backlinks, and traffic trends in one view',
      'Compare how AI platforms position your brand against rivals',
    ],
  },
  {
    id: 'content',
    label: 'Content',
    title: 'Write and optimize content faster with AI',
    bullets: [
      'Discover high-performing topics using real-time SEO and competitive data',
      'Generate full articles in your brand voice in minutes',
      'Get prioritized recommendations to make your content more visible in Google and AI search tools',
    ],
  },
  {
    id: 'links',
    label: 'Link Building',
    title: 'Grow your domain’s authority in search and AI',
    bullets: [
      'Uncover where your rivals get their best links',
      'Analyze link quality and find missed linking opportunities',
      'Audit your backlink profile to spot toxic links hurting your site',
    ],
  },
  {
    id: 'local',
    label: 'Local',
    title: 'Get found by customers in your area',
    bullets: [
      'Manage your Google Business Profile (GBP) information in one place',
      'Distribute your business info to 70+ US directories in one go',
      'Collect reviews from customers with automated SMS and email campaigns',
    ],
  },
  {
    id: 'reports',
    label: 'Reports',
    title: 'Prove your impact with exec-ready reports',
    bullets: [
      'Connect data from ZeOrbit and 35+ top marketing tools',
      'Drag and drop charts and tables — or use ready-made templates',
      'Create once, auto-update anytime you need it',
    ],
  },
]

export const HOW_IT_WORKS = [
  { id: '01', title: 'Connect your website', copy: 'Add your domain and goals so ZeOrbit can map keywords, competitors, and technical issues.' },
  { id: '02', title: 'Run the full toolkit', copy: 'Research keywords, fix site issues, create content, and track AI + Google visibility in one place.' },
  { id: '03', title: 'Prove the impact', copy: 'Share exec-ready reports that show rankings, traffic, and AI visibility growth over time.' },
]

export const PROOF_STATS = [
  { value: '28M', label: 'Marketing professionals have already used ZeOrbit' },
  { value: '21', label: 'International awards for best SEO software suite' },
  { value: '35%', label: 'Fortune 500 companies use ZeOrbit as their go-to marketing tool' },
]

export const AWARD_BADGES = [
  '#1 SEO TOOL',
  '#1 AEO TOOL',
  '#1 Competitive Intelligence',
  'Best Software Products 2026',
  'Best Global Software Companies 2026',
]

export const PRICING_TIERS = [
  {
    name: 'Starter',
    price: '$49',
    period: '/mo',
    tagline: 'Unlimited access to the ZeOrbit tools that fit your goals.',
    features: [
      'Site audit & AI search health',
      'Keyword research toolkit',
      'Rank tracking essentials',
      'AI content recommendations',
    ],
    cta: 'Try free for 7 days',
    highlighted: false,
  },
  {
    name: 'Professional',
    price: '$149',
    period: '/mo',
    tagline: 'A complete visibility management platform for growing teams.',
    features: [
      'Everything in Starter',
      'Competitive analysis & backlinks',
      'AI Visibility Score tracking',
      'Local SEO & GBP tools',
      'Exec-ready reporting',
    ],
    cta: 'Try free for 7 days',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    tagline: 'For agencies and Fortune-scale brands that need custom support.',
    features: [
      'Unlimited seats & projects',
      'Custom integrations',
      'Dedicated onboarding',
      'Priority support',
    ],
    cta: 'Contact Sales',
    highlighted: false,
  },
]

export const FAQS = [
  {
    q: 'What is included in the free trial?',
    a: 'Try free for 7 days with access to the ZeOrbit tools that fit your goals — site performance, keyword research, AI visibility, content, and more.',
  },
  {
    q: 'Is ZeOrbit only for SEO?',
    a: 'No — ZeOrbit is a complete visibility management platform spanning SEO, AI search visibility, competitive analysis, content, local, and reporting.',
  },
  {
    q: 'Can I track AI search visibility?',
    a: 'Yes. Measure how often your brand appears in AI responses, discover trending prompts, and close gaps where competitors show up.',
  },
  {
    q: 'Does ZeOrbit support local SEO?',
    a: 'Yes — manage Google Business Profile information, distribute listings, and collect reviews so customers can find you in your area.',
  },
  {
    q: 'Can I export reports for stakeholders?',
    a: 'Yes. Build exec-ready reports with drag-and-drop charts, templates, and auto-updating data.',
  },
]

export const INSIGHTS = [
  {
    category: 'AI Search',
    title: 'How AEO and GEO are changing service-business discovery',
    excerpt: 'A practical framework for visibility in AI answer engines and conversational discovery.',
  },
  {
    category: 'SEO',
    title: 'Scan your website for SEO and AI search issues',
    excerpt: 'Prioritize technical fixes that affect search and AI visibility.',
  },
  {
    category: 'Growth',
    title: 'Target the best keywords with AI',
    excerpt: 'Use volume, difficulty, intent, and AI Overview opportunities to guide strategy.',
  },
]

export const SITE_SOCIAL = [
  { label: 'Facebook', href: 'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com/company/zeorbit/' },
  { label: 'Instagram', href: 'https://www.instagram.com/zeorbit/' },
  { label: 'X', href: 'https://twitter.com/orbit_ze' },
]
