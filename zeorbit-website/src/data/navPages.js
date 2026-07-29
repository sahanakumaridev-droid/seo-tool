/** Content for each primary nav destination */

export const NAV_PAGES = {
  'website-designing': {
    slug: 'website-designing',
    navLabel: 'Website Designing',
    eyebrow: 'Web Development',
    title: 'Websites built to convert, rank, and scale with your business.',
    lead:
      'ZeOrbit designs and develops websites for U.S. companies that need more than a brochure—fast experiences, clear offers, and structure ready for SEO and AI search.',
    heroImage: '/service-website.jpg',
    accent: '#2563eb',
    highlights: [
      {
        title: 'Custom Website Design',
        copy: 'We design interfaces that explain what you sell and guide visitors to the right action.',
      },
      {
        title: 'WordPress & Web Platforms',
        copy: 'We build editable sites your team can update without waiting on engineering for every change.',
      },
      {
        title: 'Ecommerce Storefronts',
        copy: 'We structure catalogs, checkout, and performance so visits turn into completed orders.',
      },
      {
        title: 'Performance Engineering',
        copy: 'We ship with speed, Core Web Vitals, and production hardening from the first release.',
      },
    ],
    features: [
      {
        title: 'SEO- and AEO-ready architecture',
        copy: 'Information architecture, metadata, schema, and content models built for Google and AI answer engines.',
        image: '/path-website.jpg',
      },
      {
        title: 'Conversion-first UX',
        copy: 'Hierarchy, trust cues, and CTAs mapped to how U.S. buyers evaluate and buy.',
        image: '/path-grow.jpg',
      },
      {
        title: 'Hosting & ongoing care',
        copy: 'Secure hosting, updates, and monitoring so the site stays production-ready after launch.',
        image: '/service-software.jpg',
      },
    ],
    process: [
      { step: '01', title: 'Discover', copy: 'Goals, audiences, competitors, and content inventory.' },
      { step: '02', title: 'Design', copy: 'Wireframes, visual system, and interactive prototypes.' },
      { step: '03', title: 'Build', copy: 'Responsive development, CMS, analytics, and integrations.' },
      { step: '04', title: 'Launch', copy: 'QA, SEO baseline, tracking, and operator training.' },
    ],
    stats: [
      { value: 'SEO + AEO', label: 'Search architecture' },
      { value: 'Performance', label: 'First-release priority' },
      { value: 'CMS-ready', label: 'Editable after launch' },
    ],
  },

  'mobile-apps': {
    slug: 'mobile-apps',
    navLabel: 'Mobile Apps',
    eyebrow: 'Mobile App Development',
    title: 'Mobile apps engineered for real users and real operations.',
    lead:
      'ZeOrbit builds iOS, Android, and cross-platform apps with secure backends—so your product is usable in the stores and maintainable as you grow.',
    heroImage: '/service-app.jpg',
    accent: '#7c3aed',
    highlights: [
      {
        title: 'iOS App Development',
        copy: 'We build native-quality experiences for iPhone and iPad users.',
      },
      {
        title: 'Android App Development',
        copy: 'We ship stable Android products with modern UI patterns and solid release practices.',
      },
      {
        title: 'Flutter & React Native',
        copy: 'We use shared codebases when you need speed and consistency across platforms.',
      },
      {
        title: 'Backend & APIs',
        copy: 'We wire auth, payments, notifications, and cloud services correctly from day one.',
      },
    ],
    features: [
      {
        title: 'From product brief to store release',
        copy: 'Discovery, UX, engineering sprints, TestFlight / Play Console support, and launch readiness.',
        image: '/path-app.jpg',
      },
      {
        title: 'Security in the architecture',
        copy: 'Authentication, permissions, and data handling designed before features pile on.',
        image: '/path-automate.jpg',
      },
      {
        title: 'Instrumentation for iteration',
        copy: 'Events, funnels, and crash reporting so product decisions stay evidence-based.',
        image: '/path-grow.jpg',
      },
    ],
    process: [
      { step: '01', title: 'Product brief', copy: 'Scope platforms, features, and release criteria.' },
      { step: '02', title: 'UX / UI', copy: 'Flows, design system, and clickable prototypes.' },
      { step: '03', title: 'Engineering', copy: 'App and API delivery with demos each sprint.' },
      { step: '04', title: 'Ship', copy: 'Store submission, monitoring, and iteration plan.' },
    ],
    stats: [
      { value: 'iOS + Android', label: 'Platform coverage' },
      { value: 'API-backed', label: 'Product architecture' },
      { value: 'Store-ready', label: 'Release support' },
    ],
  },

  'custom-software': {
    slug: 'custom-software',
    navLabel: 'Custom Software',
    eyebrow: 'Custom Software Development',
    title: 'Custom software that matches how your business actually runs.',
    lead:
      'ZeOrbit builds secure CRMs, dashboards, and internal platforms around your workflows—so teams stop forcing processes into tools that were never meant for them.',
    heroImage: '/service-software.jpg',
    accent: '#0ea5e9',
    highlights: [
      {
        title: 'ERP & CRM Systems',
        copy: 'We build operational platforms tailored to how your teams sell and deliver.',
      },
      {
        title: 'Cloud-Native Apps',
        copy: 'We modernize, migrate, and build scalable cloud applications for growth.',
      },
      {
        title: 'API Integrations',
        copy: 'We connect payments, CRMs, ERPs, and data sources into one reliable flow.',
      },
      {
        title: 'Internal Dashboards',
        copy: 'We give operators and leaders live visibility without spreadsheet chaos.',
      },
    ],
    features: [
      {
        title: 'Architecture ready to grow',
        copy: 'Modular services and clean APIs so new channels and AI features can plug in later.',
        image: '/path-ai.jpg',
      },
      {
        title: 'Automation and AI inside the stack',
        copy: 'Workflows, alerts, and copilots that cut repetitive operator work.',
        image: '/path-automate.jpg',
      },
      {
        title: 'Security-minded delivery',
        copy: 'Access control, auditability, and hardening for systems that carry business risk.',
        image: '/service-data.jpg',
      },
    ],
    process: [
      { step: '01', title: 'Map workflows', copy: 'Document systems, bottlenecks, and data dependencies.' },
      { step: '02', title: 'Blueprint', copy: 'Architecture, roadmap, and MVP definition.' },
      { step: '03', title: 'Build & integrate', copy: 'Iterative delivery with stakeholder demos.' },
      { step: '04', title: 'Operate', copy: 'Deploy, train teams, and refine based on usage.' },
    ],
    stats: [
      { value: 'Workflow-fit', label: 'Product design' },
      { value: 'Cloud-ready', label: 'Infrastructure' },
      { value: 'API-first', label: 'Integration model' },
    ],
  },

  'seo-ppc': {
    slug: 'seo-ppc',
    navLabel: 'SEO & PPC Tactics',
    eyebrow: 'SEO · AEO · GEO · Paid Media',
    title: 'Search and paid systems that create qualified demand.',
    lead:
      'ZeOrbit combines technical SEO, AEO/GEO readiness, and paid media so U.S. brands show up in Google and AI-powered discovery—then convert that attention into leads and revenue.',
    heroImage: '/service-seo.jpg',
    accent: '#ff5a4e',
    highlights: [
      {
        title: 'Technical & On-Page SEO',
        copy: 'We improve crawl health, structure, and pages built to rank and convert.',
      },
      {
        title: 'Local & Nationwide SEO',
        copy: 'We strengthen maps, entities, and multi-location visibility for service brands.',
      },
      {
        title: 'AEO / GEO',
        copy: 'We prepare content and markup for answer engines and AI recommendations.',
      },
      {
        title: 'Paid Ads',
        copy: 'We run Google, Meta, TikTok, Pinterest, and YouTube campaigns with clean tracking.',
      },
    ],
    features: [
      {
        title: 'Organic systems that compound',
        copy: 'Keyword strategy, content architecture, and technical fixes that build durable visibility.',
        image: '/path-grow.jpg',
      },
      {
        title: 'Paid media with accountable measurement',
        copy: 'Campaign structure, creative testing, and conversion tracking tied to business outcomes.',
        image: '/path-reveal-grow.jpg',
      },
      {
        title: 'Reporting that answers “what next?”',
        copy: 'Rankings, traffic quality, leads, and revenue signals—not vanity charts.',
        image: '/service-data.jpg',
      },
    ],
    process: [
      { step: '01', title: 'Audit', copy: 'Site health, competitors, and opportunity map.' },
      { step: '02', title: 'Strategy', copy: 'Channel mix, content plan, and KPI framework.' },
      { step: '03', title: 'Execute', copy: 'Technical work, content, and campaign launches.' },
      { step: '04', title: 'Optimize', copy: 'Iterate on performance with shared reporting.' },
    ],
    stats: [
      { value: 'SEO + PPC', label: 'Demand channels' },
      { value: 'AEO / GEO', label: 'AI search readiness' },
      { value: 'Lead-focused', label: 'Measurement model' },
    ],
  },

  contact: {
    slug: 'contact',
    navLabel: 'Contact',
    eyebrow: 'Talk to ZeOrbit',
    title: 'Tell us what you want to build.',
    lead:
      'Share your AI, software, website, app, automation, or growth goals. We’ll outline clear next steps with our U.S.-based team.',
    heroImage: '/hero-agency.jpg',
    accent: '#4f46e5',
    highlights: [
      { title: 'Direct follow-up', copy: 'We respond with next steps—no spam sequences.' },
      { title: 'U.S.-based team', copy: 'Communication aligned to American business hours.' },
      { title: 'Clear scoping', copy: 'Transparent deliverables before work begins.' },
      { title: 'Call anytime', copy: '619-724-9517' },
    ],
    features: [],
    process: [],
    stats: [
      { value: '619-724-9517', label: 'Call now' },
      { value: 'info@zeorbit.com', label: 'Email' },
      { value: 'San Diego, CA', label: 'U.S. base' },
    ],
    isContact: true,
  },
}

export const SERVICE_SLUGS = Object.keys(NAV_PAGES).filter((k) => k !== 'contact')
