/** ZeOrbit free Lead Engine playbook — platforms + owned funnels (no paid APIs required). */

export const LEAD_PLATFORMS = [
  {
    name: 'Upwork',
    url: 'https://www.upwork.com',
    bestFor: 'Mobile apps, software, eCommerce',
    websiteLeads: 4,
    appLeads: 5,
    quality: 'Medium–High',
    priority: 4,
    costNote: 'Connects fee / bids',
    take: 'Strong for app & software projects',
    start: true,
  },
  {
    name: 'DesignRush',
    url: 'https://www.designrush.com',
    bestFor: 'Larger website/app agency projects',
    websiteLeads: 4,
    appLeads: 4,
    quality: 'High',
    priority: 4,
    costNote: 'Agency listing / marketplace match',
    take: 'Agency-level inbound; up to ~5 candidates matched',
    start: true,
  },
  {
    name: 'Clutch',
    url: 'https://clutch.co',
    bestFor: 'Agency credibility + inbound',
    websiteLeads: 3,
    appLeads: 4,
    quality: 'High',
    priority: 4,
    costNote: 'Profile / sponsored placements',
    take: 'Credibility first, leads second',
    start: true,
  },
  {
    name: 'LinkedIn',
    url: 'https://www.linkedin.com',
    bestFor: 'Direct B2B outreach',
    websiteLeads: 5,
    appLeads: 5,
    quality: 'High',
    priority: 5,
    costNote: 'Sales Navigator optional; outreach is free',
    take: 'Best free/high-ROI B2B channel — prioritize prospecting over ads',
    start: true,
  },
  {
    name: 'Google Ads',
    url: 'https://ads.google.com',
    bestFor: 'High-intent search (owned channel)',
    websiteLeads: 5,
    appLeads: 4,
    quality: 'High',
    priority: 5,
    costNote: 'CPC — best long-term owned channel',
    take: 'Send ads to dedicated landing pages, never the homepage',
    start: true,
  },
  {
    name: 'Guru',
    url: 'https://www.guru.com',
    bestFor: 'Web / software projects',
    websiteLeads: 3,
    appLeads: 3,
    quality: 'Medium',
    priority: 3,
    costNote: 'Bids / membership',
    take: 'Secondary marketplace — test after core channels',
    start: false,
  },
  {
    name: 'Freelancer',
    url: 'https://www.freelancer.com',
    bestFor: 'High-volume projects',
    websiteLeads: 3,
    appLeads: 3,
    quality: 'Medium',
    priority: 3,
    costNote: 'Bids / membership',
    take: 'Volume over quality — use selectively',
    start: false,
  },
  {
    name: 'PeoplePerHour',
    url: 'https://www.peopleperhour.com',
    bestFor: 'Smaller web/design projects',
    websiteLeads: 3,
    appLeads: 2,
    quality: 'Medium',
    priority: 3,
    costNote: 'Hourlies / proposals',
    take: 'OK for smaller website jobs',
    start: false,
  },
  {
    name: 'Contra',
    url: 'https://contra.com',
    bestFor: 'Design/development professionals',
    websiteLeads: 2,
    appLeads: 2,
    quality: 'Medium',
    priority: 2,
    costNote: 'Commission-free independent work',
    take: 'Lower priority for agency lead volume',
    start: false,
  },
  {
    name: 'Toptal',
    url: 'https://www.toptal.com',
    bestFor: 'Premium software talent/projects',
    websiteLeads: 2,
    appLeads: 3,
    quality: 'High',
    priority: 2,
    costNote: 'Strict screening; client-side marketplace',
    take: 'Premium only — not a volume channel',
    start: false,
  },
]

export const START_WITH = ['Upwork', 'DesignRush', 'Clutch', 'LinkedIn', 'Google Ads']

export const TRACK_METRICS = [
  'Leads received',
  'Cost per lead',
  'Qualified leads',
  'Calls booked',
  'Proposals sent',
  'Projects won',
  'Average project value',
  'Cost per acquisition',
]

export const SERVICE_FUNNELS = [
  {
    id: 'website-redesign',
    slug: '/website-redesign/',
    label: 'Website Redesign',
    headline: 'Is Your Website Looking Outdated? Get a Modern Website Redesign.',
    cta: 'Book a Free Redesign Consult',
    keywords: ['website redesign', 'website redesign company', 'outdated website redesign'],
    businessType: 'Website Redesign',
  },
  {
    id: 'small-business-web',
    slug: '/small-business-web-design/',
    label: 'Small Business Website',
    headline: 'Professional Website for Your Business — Starting Packages Available.',
    cta: 'Get a Free Website Quote',
    keywords: ['small business website', 'affordable website design', 'website designer near me'],
    businessType: 'Small Business Web Design',
  },
  {
    id: 'ecommerce',
    slug: '/ecommerce-website/',
    label: 'eCommerce',
    headline: 'Launch or Redesign Your Shopify / WooCommerce Store.',
    cta: 'Get an eCommerce Quote',
    keywords: ['ecommerce website developer', 'shopify developer', 'woocommerce developer'],
    businessType: 'eCommerce Development',
  },
  {
    id: 'mobile-app',
    slug: '/mobile-app-development/',
    label: 'Mobile App',
    headline: 'Have an App Idea? Let\'s Build Your MVP.',
    cta: 'Book a Free App Consultation',
    keywords: ['mobile app development company', 'app developer', 'build an app for my business'],
    businessType: 'Mobile App Development',
  },
  {
    id: 'wordpress',
    slug: '/wordpress-web-design/',
    label: 'WordPress',
    headline: 'Need a WordPress Expert? We Can Help.',
    cta: 'Talk to a WordPress Expert',
    keywords: ['wordpress developer near me', 'wordpress website design', 'wordpress expert'],
    businessType: 'WordPress Development',
  },
  {
    id: 'nonprofit',
    slug: '/nonprofit-church-websites/',
    label: 'Nonprofit / Church',
    headline: 'Modern Websites for Churches & Nonprofits.',
    cta: 'Request a Nonprofit Website Quote',
    keywords: ['church website design', 'nonprofit website design', 'church website developer'],
    businessType: 'Nonprofit Website Design',
  },
  {
    id: 'website-design',
    slug: '/website-design/',
    label: 'Website Design',
    headline: 'Professional Website Design for Small Businesses',
    cta: 'Get a Free Design Quote',
    keywords: ['website design company', 'website designer', 'professional website design'],
    businessType: 'Web Design',
  },
  {
    id: 'san-diego-web',
    slug: '/san-diego-web-design/',
    label: 'San Diego Web Design',
    headline: 'San Diego Website Design Company',
    cta: 'Book a Local Consult',
    keywords: ['san diego website design', 'website designer san diego', 'web design company san diego'],
    businessType: 'Web Design',
  },
  {
    id: 'ios-app',
    slug: '/ios-app-development/',
    label: 'iOS App',
    headline: 'Custom iOS App Development for Businesses & Startups',
    cta: 'Book an iOS Consult',
    keywords: ['ios app development', 'iphone app developer', 'ios app developer san diego'],
    businessType: 'iOS App Development',
  },
  {
    id: 'android-app',
    slug: '/android-app-development/',
    label: 'Android App',
    headline: 'Android App Development That Ships',
    cta: 'Book an Android Consult',
    keywords: ['android app development', 'android app developer', 'android app company'],
    businessType: 'Android App Development',
  },
  {
    id: 'app-mvp',
    slug: '/app-mvp-development/',
    label: 'App MVP',
    headline: 'Turn Your App Idea Into a Working MVP',
    cta: 'Start Your MVP',
    keywords: ['app mvp development', 'mvp app developer', 'build mvp app'],
    businessType: 'App MVP Development',
  },
  {
    id: 'app-sd',
    slug: '/app-development-san-diego/',
    label: 'San Diego Apps',
    headline: 'Mobile App Development for Businesses & Startups in San Diego',
    cta: 'Book a Free App Consultation',
    keywords: ['app developer san diego', 'mobile app development san diego'],
    businessType: 'Mobile App Development',
  },
]

export const QUOTE_STEPS = {
  services: [
    { id: 'new-website', label: 'New Website' },
    { id: 'website-redesign', label: 'Website Redesign' },
    { id: 'ecommerce', label: 'eCommerce' },
    { id: 'mobile-app', label: 'Mobile App' },
    { id: 'wordpress', label: 'WordPress' },
    { id: 'seo', label: 'SEO' },
    { id: 'other', label: 'Other' },
  ],
  budgets: [
    'Under $1,000',
    '$1,000–$2,500',
    '$2,500–$5,000',
    '$5,000–$10,000',
    '$10,000+',
  ],
  timelines: [
    'ASAP',
    'Within 30 days',
    '1–3 months',
    'Just researching',
  ],
}

export const GOOGLE_ADS_KEYWORDS = [
  'website designer near me',
  'website design company',
  'website redesign company',
  'WordPress developer near me',
  'ecommerce website developer',
  'mobile app development company',
  'app developer San Diego',
  'build an app for my business',
]

export const LOCAL_SEO_CITIES = [
  'San Diego', 'Chula Vista', 'La Mesa', 'El Cajon', 'Carlsbad',
  'Escondido', 'Oceanside', 'Coronado', 'Encinitas', 'Santee', 'Poway',
]

export const LOCAL_SEO_PAGES = [
  'San Diego Website Design',
  'San Diego WordPress Development',
  'San Diego Mobile App Development',
  'San Diego eCommerce Development',
]

export const LINKEDIN_TARGETS = [
  'Business owners', 'Founders', 'CEOs', 'Marketing Directors',
  'Practice owners', 'Contractors', 'Real estate companies',
  'Medical practices', 'Churches / nonprofits', 'Restaurants', 'Professional services',
]

export const LINKEDIN_MESSAGE =
  'I noticed your website could use a modern refresh. We help businesses redesign outdated websites while improving mobile experience and conversions.'

export const BUDGET_PLAN = [
  { channel: 'Google Search Ads', pct: 50, amount: 1500, note: 'High-intent searches → dedicated LPs' },
  { channel: 'Upwork / DesignRush', pct: 25, amount: 750, note: 'Marketplace project opportunities' },
  { channel: 'LinkedIn prospecting', pct: 10, amount: 300, note: 'Tools + outreach time' },
  { channel: 'Landing pages / SEO content', pct: 8, amount: 250, note: 'Build owned assets in this tool' },
  { channel: 'Retargeting / testing', pct: 7, amount: 200, note: 'Iterate after 60 days' },
]

export const ENGINE_STACK = [
  { name: 'Google Ads', role: 'High-intent leads' },
  { name: 'Local SEO', role: 'Free recurring leads' },
  { name: 'LinkedIn outreach', role: 'B2B / high-value' },
  { name: 'Upwork', role: 'App / software opportunities' },
  { name: 'DesignRush / Clutch', role: 'Larger agency opportunities' },
  { name: 'Referrals', role: 'Highest-quality leads' },
]

export const SALES_FUNNEL = ['Lead', 'Qualification', '15-min Call', 'Proposal', 'Deposit', 'Project']

export const SPEED_RULE =
  'Respond within 5–15 minutes during business hours with a short personalized message — not a generic sales pitch. Speed wins qualified leads.'
