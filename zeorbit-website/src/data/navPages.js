/** Content for each primary nav destination — unique per page, no shared filler. */

export const NAV_PAGES = {
  'mobile-apps': {
    slug: 'mobile-apps',
    navLabel: 'Mobile Apps',
    brand: 'ZeOrbit',
    eyebrow: 'Mobile Apps · iOS & Android',
    title: 'Apps that feel native — and ship store-ready.',
    lead:
      'From first wireframe to App Store and Google Play. ZeOrbit designs and builds mobile products U.S. teams can launch, measure, and grow.',
    image: '/showcase/mobile-lifestyle.webp',
    heroTone: 'light',
    proof: ['iOS', 'Android', 'Flutter', 'React Native', 'Store launch', 'San Diego HQ'],
    manifesto: {
      title: 'We’re building the future of applications — smart, interconnected, and designed to simplify your life.',
      line: 'We design & develop mobile apps for iOS, Android, and cross-platform.',
    },
    deliverables: {
      kicker: 'Deliverables',
      title: 'What we can do for you',
      lead: 'Modern tools and a proven process to build mobile apps that perform and scale.',
      items: [
        { icon: 'Search', title: 'Ideation & Discovery', copy: 'Research market needs, define core features.' },
        { icon: 'PenTool', title: 'Client-Centric Design', copy: 'User-friendly UI and prototypes for testing.' },
        { icon: 'GitBranch', title: 'Agile Development', copy: 'Collaborate, integrate, and test continuously.' },
        { icon: 'BadgeCheck', title: 'Quality Assurance', copy: 'Fix bugs, optimize speed and stability.' },
        { icon: 'Rocket', title: 'Deployment & Launch', copy: 'Submit, market, and refine with feedback.' },
        { icon: 'Shield', title: 'Data Security', copy: 'Protect user data and stay compliant.' },
        { icon: 'Server', title: 'Backend Development', copy: 'Build scalable, high-performance systems.' },
        { icon: 'LineChart', title: 'Analytics & Monitoring', copy: 'Track performance and improve the experience.' },
      ],
    },
    stack: {
      kicker: 'Technology Stack',
      lead: 'Powerful, scalable, secure apps — using the tools that fit the product, not a one-size stack.',
      groups: [
        {
          title: 'Mobile App Development',
          lines: ['iOS: Swift, SwiftUI, Objective-C', 'Android: Kotlin, Java', 'Cross-platform: Flutter, React Native'],
        },
        {
          title: 'Backend Development',
          lines: ['Node.js, Python (Django / Flask)', 'PHP (Laravel), .NET Core', 'Ruby on Rails'],
        },
        {
          title: 'Frontend & Web',
          lines: ['React.js, Next.js', 'Angular, Vue.js', 'HTML5, CSS3'],
        },
        {
          title: 'Database',
          lines: ['MySQL, PostgreSQL', 'MongoDB, Firebase', 'SQLite'],
        },
        {
          title: 'Cloud & DevOps',
          lines: ['AWS, Google Cloud, Azure', 'Docker, Kubernetes'],
        },
        {
          title: 'Tools & Integrations',
          lines: ['GitHub, Bitbucket, Jira', 'Figma, Postman', 'Firebase Analytics'],
        },
      ],
    },
    unique: {
      kicker: 'What makes us unique',
      title: 'Built around the outcome, not the stack.',
      items: [
        { title: 'Launch new products', copy: 'Android and iOS apps shaped around the business you want to run next.' },
        { title: 'Validate ideas', copy: 'Prototype, test, and refine before you spend the full build budget.' },
        { title: 'Improve KPIs', copy: 'Instrumentation and iteration so performance keeps moving after launch.' },
        { title: 'Tailored solutions', copy: 'Custom apps, backends, and software that fit how your team actually works.' },
      ],
    },
    services: [
      {
        id: 'native',
        kicker: 'iOS & Android',
        title: 'Native iOS and Android apps.',
        copy: 'Store-ready apps with native performance, clear UX, and a release process U.S. teams can trust — from TestFlight and Play Console through launch.',
        points: ['Swift / Kotlin or high-quality native shells', 'App Store and Google Play submission', 'Push, payments, and device APIs', 'Crash monitoring after launch'],
        image: '/showcase/mobile-phones-grid.png',
        cta: 'Start an iOS / Android brief',
      },
      {
        id: 'cross',
        kicker: 'Cross-platform',
        title: 'One codebase for both stores.',
        copy: 'Flutter or React Native when you need iOS and Android without shipping two generic apps. Shared logic, platform-aware UI.',
        points: ['Flutter or React Native', 'Shared design system', 'Native modules where it matters', 'One QA and release cadence'],
        image: '/showcase/mobile-phones-fan.webp',
        cta: 'Discuss cross-platform',
      },
      {
        id: 'timeline',
        kicker: 'App Timeline',
        title: 'A clear path from brief to store.',
        copy: 'Discovery, design, build, and launch on a schedule stakeholders can follow — with demos you can tap, not slide decks.',
        points: ['Week-by-week milestones', 'Design and engineering overlap', 'TestFlight / internal testing', 'Store listing and launch week'],
        image: '/showcase/mobile-phones-grid.png',
        cta: 'See a sample timeline',
      },
      {
        id: 'ux',
        kicker: 'Mobile UX / UI',
        title: 'Interfaces built for thumbs.',
        copy: 'Flows, visual system, and prototypes designed around the one action that matters — fast, readable, and easy to ship.',
        points: ['User flows and wireframes', 'High-fidelity UI', 'Clickable prototypes', 'Handoff ready for engineering'],
        image: '/showcase/hero-ui-float.png',
        cta: 'Improve app UX',
      },
      {
        id: 'backend',
        kicker: 'Backends & APIs',
        title: 'The stack behind the app.',
        copy: 'Auth, payments, push notifications, and cloud services wired correctly from day one.',
        image: '/showcase/ai-ops-dark.png',
        cta: 'Plan the architecture',
      },
      {
        id: 'care',
        kicker: 'Updates & care',
        title: 'Keep the app healthy after launch.',
        copy: 'OS updates, crash monitoring, feature iterations, and store compliance so the product does not stall after day one.',
        image: '/showcase/pro/web-design-mac.jpg',
        cta: 'Keep my app healthy',
      },
    ],
    work: [
      {
        title: 'Consumer mobile products',
        meta: 'iOS · Android · UX',
        image: '/showcase/mobile-single.png',
      },
      {
        title: 'Service & field apps',
        meta: 'Offline-ready · APIs',
        image: '/showcase/mobile-dark-phone.png',
      },
      {
        title: 'Launch dashboards',
        meta: 'Analytics · Retention',
        image: '/showcase/work-minimal.png',
      },
      {
        title: 'Store-ready packaging',
        meta: 'Listing · Screenshots',
        image: '/showcase/cta-phone.png',
      },
    ],
    process: [
      { num: '01', title: 'Brief', copy: 'Platforms, must-have features, and success metrics.' },
      { num: '02', title: 'Design', copy: 'Flows, UI system, and clickable prototypes.' },
      { num: '03', title: 'Build', copy: 'App + API sprints with demos you can tap.' },
      { num: '04', title: 'Ship', copy: 'Store submission, monitoring, and iteration plan.' },
    ],
    growth: {
      kicker: 'Built to iterate',
      title: 'Instrumentation from the first release.',
      lead: 'Events, funnels, and crash reporting so product decisions stay evidence-based — not guesswork.',
      metrics: [
        { label: 'Crash-free', value: '99.8%' },
        { label: 'Funnel lift', value: '+24%' },
        { label: 'Store rating', value: '4.9' },
        { label: 'Time to signal', value: '7d' },
      ],
      points: [
        'Analytics & funnel tracking',
        'Crash & performance monitoring',
        'Push & lifecycle messaging',
        'Store review readiness',
      ],
      cta: 'Plan my app launch',
    },
    faqs: [
      {
        q: 'How long does a mobile app take?',
        a: 'Most MVPs ship in 8–16 weeks depending on features, integrations, and design scope. You get a timeline before engineering starts.',
      },
      {
        q: 'Native or cross-platform?',
        a: 'We recommend based on UX needs, budget, and team. Many products start cross-platform; some need native for performance or platform-specific features.',
      },
      {
        q: 'Do you help with App Store and Google Play?',
        a: 'Yes — listing assets, compliance checks, TestFlight / Play Console, and submission support.',
      },
      {
        q: 'Can you connect to our existing systems?',
        a: 'Yes. We integrate CRMs, payments, auth providers, and internal APIs as part of the build.',
      },
      {
        q: 'What happens after launch?',
        a: 'We can stay on for updates, OS changes, analytics reviews, and new feature sprints.',
      },
      {
        q: 'How do we start?',
        a: 'Share a short product brief or call 619-724-9517. We’ll reply with scope options and next steps.',
      },
    ],
    finalCta: {
      kicker: 'Start an app project',
      title: 'Tell us what the app needs to do.',
      lead: 'Platforms, users, and must-have features — we’ll map a realistic build plan.',
    },
  },

  'seo-ppc': {
    slug: 'seo-ppc',
    navLabel: 'SEO & Ads',
    brand: 'ZeOrbit',
    eyebrow: 'SEO · GEO · Paid Media',
    title: 'Get found. Get chosen. Get measured.',
    lead:
      'Technical SEO, local visibility, content systems, and paid ads — built so U.S. businesses attract qualified demand, not vanity traffic.',
    image: '/showcase/pro/commerce-laptop.jpg',
    heroTone: 'light',
    proof: ['SEO', 'Local SEO', 'Google Ads', 'Meta Ads', 'YouTube', 'AEO / GEO'],
    services: [
      {
        id: 'seo',
        kicker: 'Technical SEO',
        title: 'Technical and on-page SEO.',
        copy: 'Crawl health, structure, Core Web Vitals, and pages built to rank and convert — not just to look optimized.',
        points: ['Site audit and crawl fixes', 'Core Web Vitals', 'On-page titles, headers, internal links', 'Schema markup'],
        image: '/showcase/pro/web-ui-desk.jpg',
        cta: 'Audit my site',
      },
      {
        id: 'local',
        kicker: 'Local SEO',
        title: 'Get found in the cities you serve.',
        copy: 'Maps, Google Business Profile, and location pages so nearby customers choose you — not a competitor down the street.',
        points: ['Google Business Profile', 'Local citations', 'City and service-area pages', 'Review strategy'],
        image: '/showcase/pro/commerce-ui-b.jpg',
        cta: 'Grow local search',
      },
      {
        id: 'content',
        kicker: 'Content SEO',
        title: 'Topic clusters that compound.',
        copy: 'Editorial systems and pages written to rank for the queries your buyers actually type.',
        points: ['Keyword mapping', 'Cluster architecture', 'On-page briefs', 'Publish cadence'],
        image: '/showcase/pro/graphic-palette.jpg',
        cta: 'Plan content SEO',
      },
      {
        id: 'ads',
        kicker: 'Google Ads',
        title: 'Search ads tied to real leads.',
        copy: 'Account structure, tracking, and landing pages so spend produces inquiries — not vanity clicks.',
        points: ['Search campaigns', 'Conversion tracking', 'Landing page CRO', 'Budget control'],
        image: '/showcase/work-ui.png',
        cta: 'Launch Google Ads',
      },
      {
        id: 'social-ads',
        kicker: 'Social Ads',
        title: 'Meta, TikTok, and Pinterest ads.',
        copy: 'Creative testing and audiences built from your customers — for demand on the platforms they already use.',
        points: ['Meta campaigns', 'TikTok and Pinterest', 'Creative sprints', 'Pixel / CAPI tracking'],
        image: '/showcase/work-hand.png',
        cta: 'Scale social ads',
      },
      {
        id: 'blog',
        kicker: 'Blog & Insights',
        title: 'A blog that actually supports SEO.',
        copy: 'Articles, internal linking, and a publishing workflow that builds authority instead of random posts.',
        points: ['Editorial calendar', 'SEO-backed articles', 'Internal linking', 'Insights your team can share'],
        image: '/showcase/web-browser-cases.png',
        cta: 'Plan the blog',
      },
    ],
    work: [
      {
        title: 'Performance reporting',
        meta: 'SEO · Ads · Dashboards',
        image: '/showcase/ux-designer-desk.png',
      },
      {
        title: 'Local growth systems',
        meta: 'Maps · Landing pages',
        image: '/showcase/pro/web-laptop-desk.jpg',
      },
      {
        title: 'Conversion landing pages',
        meta: 'PPC · CRO',
        image: '/showcase/pro/commerce-ui-a.jpg',
      },
      {
        title: 'Content engines',
        meta: 'Blog · Clusters',
        image: '/showcase/web-browser-cases.png',
      },
    ],
    process: [
      { num: '01', title: 'Audit', copy: 'Site health, competitors, and opportunity map.' },
      { num: '02', title: 'Strategy', copy: 'Channel mix, content plan, and KPI framework.' },
      { num: '03', title: 'Execute', copy: 'Technical work, content, and campaign launches.' },
      { num: '04', title: 'Optimize', copy: 'Iterate with shared reporting — not vanity charts.' },
    ],
    growth: {
      kicker: 'Accountable growth',
      title: 'Reporting that answers “what next?”',
      lead: 'Rankings, traffic quality, leads, and revenue signals — so budget follows what works.',
      metrics: [
        { label: 'Qualified leads', value: '+38%' },
        { label: 'Ranked terms', value: '214' },
        { label: 'CPL', value: '−19%' },
        { label: 'Map views', value: '+2.1×' },
      ],
      points: [
        'Keyword & ranking systems',
        'Conversion tracking',
        'Creative & landing tests',
        'Monthly action plans',
      ],
      cta: 'Get a growth plan',
    },
    faqs: [
      {
        q: 'How soon can SEO show results?',
        a: 'Technical fixes can help quickly; durable ranking growth usually compounds over months. We set expectations by competitive landscape.',
      },
      {
        q: 'Do you manage Google Ads?',
        a: 'Yes — account structure, creative testing, conversion tracking, and ongoing optimization.',
      },
      {
        q: 'Can you help multi-location businesses?',
        a: 'Yes. We build local landing systems, maps optimization, and location-aware content.',
      },
      {
        q: 'What is AEO / GEO?',
        a: 'Preparing your site and content so AI-powered search and answer experiences can cite and recommend you accurately.',
      },
      {
        q: 'Do you work with our existing website?',
        a: 'Yes. We can improve what you have or pair growth work with a redesign when the site is holding you back.',
      },
      {
        q: 'How do we start?',
        a: 'Request a free audit-style consult or call 619-724-9517. We’ll outline priorities and a clear first month.',
      },
    ],
    finalCta: {
      kicker: 'Start SEO or ads',
      title: 'Tell us where you need demand.',
      lead: 'Organic, local, paid, or all three — we’ll recommend a focused plan for your market.',
    },
  },

  'custom-software': {
    slug: 'custom-software',
    navLabel: 'Software',
    brand: 'ZeOrbit',
    eyebrow: 'Custom Software · Automation',
    title: 'Software that matches how your business actually runs.',
    lead:
      'CRMs, dashboards, integrations, and practical automation — built around your workflows so teams stop forcing work into tools that were never meant for them.',
    image: '/showcase/work-mac-stone.png',
    heroTone: 'dark',
    proof: ['Dashboards', 'CRM / ERP', 'APIs', 'Automation', 'Cloud', 'AI when needed'],
    services: [
      {
        id: 'platforms',
        kicker: 'Dashboards',
        title: 'Dashboards and internal tools.',
        copy: 'Live visibility for operators and leaders — without spreadsheet chaos.',
        image: '/showcase/growth-dashboard-a.png',
        cta: 'Build a dashboard',
      },
      {
        id: 'crm',
        kicker: 'CRM & Workflows',
        title: 'CRM built around how you actually sell.',
        copy: 'Operational platforms tailored to how your teams sell, deliver, and support.',
        image: '/showcase/ai-saas-purple.png',
        cta: 'Map my workflows',
      },
      {
        id: 'integrations',
        kicker: 'API Integrations',
        title: 'Connect the tools you already use.',
        copy: 'Payments, CRMs, ERPs, and data sources connected into one reliable flow.',
        image: '/showcase/pro/ux-app-prototype.jpg',
        cta: 'Connect my stack',
      },
      {
        id: 'automation',
        kicker: 'Automation',
        title: 'Workflows that cut repetitive work.',
        copy: 'Alerts, copilots, and practical automation so operators stop copy-pasting between systems.',
        image: '/showcase/ai-ops-dark.png',
        cta: 'Automate a process',
      },
      {
        id: 'cloud',
        kicker: 'Cloud',
        title: 'Cloud-native apps',
        copy: 'Modernize, migrate, and build scalable applications ready for growth.',
        image: '/showcase/web-components-iso.png',
        cta: 'Plan a cloud build',
      },
      {
        id: 'security',
        kicker: 'Security',
        title: 'Secure delivery',
        copy: 'Access control, auditability, and hardening for systems that carry business risk.',
        image: '/showcase/work-product.png',
        cta: 'Discuss security needs',
      },
    ],
    work: [
      {
        title: 'Operator dashboards',
        meta: 'Data · Role-based access',
        image: '/showcase/ux-designer-desk.png',
      },
      {
        title: 'Automation systems',
        meta: 'APIs · Workflows',
        image: '/showcase/pro/ux-app-prototype.jpg',
      },
      {
        title: 'Customer portals',
        meta: 'Auth · Self-serve',
        image: '/showcase/hero-devices-product.webp',
      },
      {
        title: 'Internal SaaS tools',
        meta: 'Cloud · Integrations',
        image: '/showcase/pro/web-design-mac.jpg',
      },
    ],
    process: [
      { num: '01', title: 'Map', copy: 'Document systems, bottlenecks, and data dependencies.' },
      { num: '02', title: 'Blueprint', copy: 'Architecture, roadmap, and MVP definition.' },
      { num: '03', title: 'Build', copy: 'Iterative delivery with stakeholder demos.' },
      { num: '04', title: 'Operate', copy: 'Deploy, train teams, and refine from real usage.' },
    ],
    growth: {
      kicker: 'Built to expand',
      title: 'Architecture ready for the next channel.',
      lead: 'Modular services and clean APIs so new products, portals, and AI features can plug in later.',
      metrics: [
        { label: 'API uptime', value: '99.95%' },
        { label: 'Integrations', value: '12' },
        { label: 'Deploys / week', value: '6' },
        { label: 'Mean restore', value: '14m' },
      ],
      points: [
        'API-first design',
        'Role-based access',
        'Audit-friendly logging',
        'Room for AI features later',
      ],
      cta: 'Scope custom software',
    },
    faqs: [
      {
        q: 'Build vs buy?',
        a: 'If a SaaS tool fits 80%+ of the need, we often recommend buying. We build when your workflow is the advantage — or the off-the-shelf path creates more friction than it solves.',
      },
      {
        q: 'How long is an MVP?',
        a: 'Many internal tools launch in 4–12 weeks depending on integrations and complexity.',
      },
      {
        q: 'Can you integrate with Salesforce, HubSpot, or Stripe?',
        a: 'Yes. Integrations are a core part of most builds we ship.',
      },
      {
        q: 'Do you add AI to every project?',
        a: 'No. We add AI when it removes real work — not as a buzzword layer.',
      },
      {
        q: 'Who owns the code?',
        a: 'You do. We document handoff so your team (or ours) can maintain it.',
      },
      {
        q: 'How do we start?',
        a: 'Share the workflow you’re trying to fix. We’ll propose an MVP scope and timeline.',
      },
    ],
    finalCta: {
      kicker: 'Start a software project',
      title: 'Describe the workflow. We’ll design the system.',
      lead: 'Dashboards, CRM, automation, or integrations — we’ll recommend the smallest useful build.',
    },
  },

  contact: {
    slug: 'contact',
    navLabel: 'Contact',
    eyebrow: 'Get in touch',
    title: 'Contact',
    lead: 'Feel free to contact us. ZeOrbit is a U.S.-based web design and IT company in San Diego — serving clients nationwide.',
    isContact: true,
    areas: {
      title: 'Areas we serve',
      lead: 'San Diego HQ — working with brands across California and nationwide.',
      items: [
        'San Diego, CA',
        'Los Angeles, CA',
        'El Cajon, CA',
        'Orange County',
        'California',
        'Texas',
        'Florida',
        'New York',
        'Arizona',
        'Nationwide U.S.',
      ],
    },
  },
}

export const SERVICE_SLUGS = Object.keys(NAV_PAGES).filter((k) => k !== 'contact')
