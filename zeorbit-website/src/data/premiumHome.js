/** Cinematic homepage — product-launch storytelling + curated showcase imagery. */

export const HERO = {
  brand: 'ZeOrbit',
  eyebrow: 'Web · Apps · Growth',
  headline: 'Digital Solutions\nThat Drive Results.',
  line: 'Websites, apps, SEO, and custom software that help ambitious brands stand out, get found, and grow — wherever your customers are.',
  primaryCta: 'Get Started',
  primaryHref: '#contact',
  scene: '/videos/hero-agency-poster.jpg',
  sceneAlt: 'ZeOrbit web design agency cinematic brand film',
  video: '/videos/hero-agency.mp4',
}

/**
 * Premium service flow after hero.
 * Clear alternating story (websites → apps → SEO → software) — no numbers.
 */
export const SERVICE_FLOW = {
  kicker: 'What we build',
  title: 'A clear path from idea to growth.',
  line: 'Four focused capabilities — so you always know what ZeOrbit delivers next.',
  items: [
    {
      id: 'websites',
      label: 'Web Design',
      title: 'Beautiful. Fast. Built to convert.',
      line: 'Custom WordPress, Shopify, and high-converting sites — clear offers, fast load, SEO ready from day one.',
      href: '/website-designing',
      cta: 'Explore websites',
      mediaType: 'video',
      media: '/videos/section-agency.mp4',
      poster: '/videos/section-agency-poster.jpg',
      tone: 'light',
      flip: false,
    },
    {
      id: 'apps',
      label: 'App Design',
      title: 'Mobile experiences customers love using.',
      line: 'iOS and Android products with polished UX, solid backends, and store-ready delivery.',
      href: '/mobile-apps',
      cta: 'Explore apps',
      mediaType: 'image',
      media: '/showcase/mobile-phones-fan.webp',
      poster: '/showcase/mobile-phones-fan.webp',
      tone: 'snow',
      flip: true,
    },
    {
      id: 'seo',
      label: 'SEO & Ads',
      title: 'SEO that gets you found.',
      line: 'Higher rankings, more traffic, more customers — with paid campaigns when you need demand faster.',
      href: '/seo-ppc',
      cta: 'Explore SEO',
      mediaType: 'image',
      media: '/showcase/growth-charts-blue.png',
      poster: '/showcase/growth-charts-blue.png',
      tone: 'light',
      flip: false,
    },
    {
      id: 'software',
      label: 'Custom Software',
      title: 'Systems that run the business.',
      line: 'Dashboards, CRM workflows, APIs, and automation tailored to how your teams actually work.',
      href: '/custom-software',
      cta: 'Explore software',
      mediaType: 'video',
      media: '/videos/hero-devices.mp4',
      poster: '/showcase/hero-devices-product.webp',
      tone: 'dark',
      flip: true,
    },
  ],
}

/** @deprecated — prefer SERVICE_FLOW */
export const CAPABILITY_STAGE = SERVICE_FLOW

/** @deprecated */
export const SERVICE_STRIPS = []

/** Studio story panels — used mid-page, never right after hero. */
export const FILM_PANELS = {
  afterWork: {
    id: 'craft',
    label: 'Website Craft',
    title: 'Designed to convert.\nBuilt to last.',
    line: 'Premium WordPress, Shopify, and custom websites for brands that need to look sharp and sell.',
    href: '/website-designing',
    cta: 'See website craft',
    mediaType: 'image',
    media: '/showcase/pro/web-design-mac.jpg',
    poster: '/showcase/pro/web-design-mac.jpg',
  },
  beforeReviews: {
    id: 'growth',
    label: 'Digital Marketing',
    title: 'Get found.\nGet chosen.',
    line: 'SEO, ads, and growth strategies that put the right customers in front of your business.',
    href: '/seo-ppc',
    cta: 'Explore growth',
    mediaType: 'image',
    media: '/showcase/growth-charts-blue.png',
    poster: '/showcase/growth-charts-blue.png',
  },
}

export const INDUSTRIES = {
  kicker: 'Industries We Serve',
  title: 'We understand your industry — and how to grow it.',
  line: 'Focused on digital growth and consumer engagement — helping brands transform how they show up online.',
  tabs: [
    {
      id: 'business',
      label: 'Business',
      items: [
        {
          icon: 'Factory',
          label: 'Manufacturing',
          blurb: 'Product sites, dealer portals, and lead systems that turn industrial demand into booked conversations.',
        },
        {
          icon: 'Scale',
          label: 'Law',
          blurb: 'Authority-building websites, practice pages, and intake flows designed for trust and qualified case leads.',
        },
        {
          icon: 'MapPin',
          label: 'Local Commercial',
          blurb: 'Local SEO, service-area pages, and conversion paths that help nearby customers find and choose you.',
        },
        {
          icon: 'MessagesSquare',
          label: 'Consultants',
          blurb: 'Clear positioning, booking-ready sites, and content systems that turn expertise into pipeline.',
        },
        {
          icon: 'HardHat',
          label: 'Construction',
          blurb: 'Project showcases, service pages, and mobile-first sites that win bids and inbound estimate requests.',
        },
        {
          icon: 'HandHeart',
          label: 'Non Profit',
          blurb: 'Mission-led websites, donation paths, and storytelling that grows supporters and community impact.',
        },
      ],
    },
    {
      id: 'consumer',
      label: 'Consumer',
      items: [
        {
          icon: 'UtensilsCrossed',
          label: 'Food & Beverage',
          blurb: 'Menus, locations, ordering paths, and brand sites that drive foot traffic and repeat customers.',
        },
        {
          icon: 'Car',
          label: 'Automotive',
          blurb: 'Inventory-ready sites, service booking, and local visibility for dealerships and auto businesses.',
        },
        {
          icon: 'Home',
          label: 'Real Estate',
          blurb: 'Listing-ready experiences, agent branding, and lead capture built for serious buyer and seller intent.',
        },
        {
          icon: 'Scissors',
          label: 'Beauty',
          blurb: 'Booking-first sites, service menus, and polished branding that turns browsers into appointments.',
        },
        {
          icon: 'Dumbbell',
          label: 'Gym & Fitness',
          blurb: 'Membership funnels, class schedules, and mobile experiences that convert trials into members.',
        },
        {
          icon: 'Leaf',
          label: 'CBD',
          blurb: 'Compliant storefronts, education content, and ecommerce flows built for discovery and trust.',
        },
      ],
    },
    {
      id: 'health',
      label: 'Health',
      items: [
        {
          icon: 'HeartPulse',
          label: 'Medical',
          blurb: 'Patient-first websites, specialty pages, and appointment paths that grow practice visibility.',
        },
        {
          icon: 'Smile',
          label: 'Dental',
          blurb: 'Clean clinic sites, treatment pages, and booking UX that makes choosing your practice easy.',
        },
        {
          icon: 'Shield',
          label: 'Insurance',
          blurb: 'Quote-ready pages, trust content, and local SEO that helps clients compare and convert.',
        },
      ],
    },
    {
      id: 'tech',
      label: 'Tech & Travel',
      items: [
        {
          icon: 'LineChart',
          label: 'SaaS & Tech',
          blurb: 'Product sites, demo funnels, and growth systems that turn visitors into qualified product-led demand.',
        },
        {
          icon: 'Cpu',
          label: 'IT',
          blurb: 'Service packaging, case studies, and lead engines for MSPs and technology providers.',
        },
        {
          icon: 'Plane',
          label: 'Tour & Travel',
          blurb: 'Itinerary-led sites, booking journeys, and visuals that inspire travelers to reserve.',
        },
        {
          icon: 'CalendarDays',
          label: 'Event Management',
          blurb: 'Event pages, registration flows, and brand systems that sell out experiences.',
        },
        {
          icon: 'Music',
          label: 'Artists',
          blurb: 'Portfolio sites, release pages, and fan funnels that grow audiences and bookings.',
        },
        {
          icon: 'GraduationCap',
          label: 'Education',
          blurb: 'Program pages, enrollment paths, and content hubs that help students take the next step.',
        },
      ],
    },
  ],
}

export const INTRO = {
  headline: 'Built for brands\nthat mean business.',
  line: 'ZeOrbit builds websites, apps, and growth systems for ambitious companies — with hands-on strategy from first sketch to launch.',
}

export const PORTFOLIO = {
  kicker: 'Selected Work',
  headline: 'Work that performs.',
  items: [
    {
      num: '01',
      title: 'Premium websites',
      meta: 'WordPress · Shopify · Custom web',
      copy: 'High-converting sites with clear structure, fast load times, and SEO baked in from day one — built for brands that need to look premium and sell.',
      result: 'Launch-ready in weeks, not months',
      image: '/showcase/pro/web-design-mac.jpg',
      alt: 'Premium website shown on MacBook',
      href: '/website-designing',
      tone: 'dark',
      flip: false,
    },
    {
      num: '02',
      title: 'Mobile products',
      meta: 'iOS · Android · Cross-platform',
      copy: 'Native and cross-platform apps with real backends, clean UX, and App Store–ready delivery — so your product feels as polished as the brand behind it.',
      result: 'From wireframe to store listing',
      image: '/showcase/mobile-lifestyle.webp',
      alt: 'Mobile app and website on phone and laptop',
      href: '/mobile-apps',
      tone: 'light',
      flip: true,
    },
    {
      num: '03',
      title: 'Ecommerce stores',
      meta: 'Shopify · WooCommerce · Payments',
      copy: 'Ecommerce experiences that make browsing effortless — collections, product pages, and checkout flows designed to turn visitors into paying customers.',
      result: 'Built to convert on every device',
      image: '/showcase/pro/commerce-devices.jpg',
      alt: 'Professional ecommerce store on multiple devices',
      href: '/website-designing',
      tone: 'dark',
      flip: true,
    },
    {
      num: '04',
      title: 'Growth systems',
      meta: 'SEO · Ads · Analytics',
      copy: 'Technical SEO, paid media, and reporting dashboards that show what is working — so you can double down on channels that bring qualified leads.',
      result: 'Traffic you can measure and scale',
      image: '/showcase/growth-charts-blue.png',
      alt: 'SEO and analytics growth dashboard',
      href: '/seo-ppc',
      tone: 'dark',
      flip: true,
    },
  ],
}

export const FINAL_CTA = {
  headline: "WHEN YOU'RE READY\nFOR WHAT'S NEXT.",
  line: 'It begins with a conversation. Tell us about your business and goals — we’ll scope a website, app, or full digital package, then follow up within one business day.',
}

/**
 * Solution-based agency band (SeekNEO-style wings section, below specializations).
 */
export const AGENCY_BAND = {
  title: 'Solution-Based Digital Marketing Agency',
  line: 'ZeOrbit is a top-notch digital partner for ambitious brands — websites, SEO, paid media, and growth systems tailored to your goals at clear, fair pricing.',
  cta: 'Know More',
  href: '/seo-ppc',
  image: '/showcase/agency-wings.webp',
}

/**
 * Why choose us — black band above Google reviews.
 */
export const WHY_CHOOSE = {
  titleLead: 'Why to',
  titleAccent: 'choose US?',
  line: 'We focus on delivering industry-feasible web applications, mobile apps, and websites. Our branding and growth work has helped many businesses hit their sales goals — and we keep adding more.',
  cta: 'Request Quote!',
  image: '/showcase/why-choose-bulbs.webp',
}

/**
 * Founded / impact band — below Why Choose Us.
 */
export const IMPACT_BAND = {
  titleLead: '2010',
  titleRest: 'ZeOrbit was founded',
  line: 'ZeOrbit represents the connected world — innovative, customer-centric digital experiences that help enterprises, teams, and communities rise.',
  cta: 'Request Quote!',
  stats: [
    { value: '16+', label: 'Years running successfully' },
    { value: 'Global', label: 'Client presence' },
    { value: '600+', label: 'Happy clients' },
    { value: '05', label: 'Recognitions' },
  ],
}

/**
 * Culture / explore band — cinematic people story.
 */
export const EXPLORE_BAND = {
  title: 'We explore and become more',
  tagLead: '#LoveToBe',
  tagBrand: 'ZeOrbit',
  line: 'We truly believe that technology makes it possible — but it’s people who make it happen.',
  cta: 'Explore',
  href: '/contact',
  image: '/videos/explore-cinematic-poster.jpg',
  video: '/videos/explore-cinematic.mp4',
  poster: '/videos/explore-cinematic-poster.jpg',
}

/**
 * OUR SPECIALIZATIONS — SeekNEO-style carousel (above Our Solutions).
 */
export const OUR_SPECIALIZATIONS = {
  titleLead: 'Our',
  titleRest: 'Specializations',
  line: 'ZeOrbit builds WordPress, Shopify, and custom digital products for ambitious brands — clear strategy, sharp craft, and hands-on delivery from first sketch through launch and scale.',
  cta: 'Request Quote',
  ctaHref: '#contact',
  items: [
    {
      id: 'web',
      title: 'Website Design',
      line: 'High-converting custom sites — clear offers, fast load, and SEO-ready structure from day one.',
      href: '/website-designing',
      image: '/showcase/pro/web-design-mac.jpg',
    },
    {
      id: 'wordpress',
      title: 'WordPress Development',
      line: 'Custom WordPress sites built for growth and lead generation — fast, SEO-ready, and easy for your team to manage.',
      href: '/website-designing#business',
      image: '/from-zeorbit/services/wordpress.jpg',
    },
    {
      id: 'app',
      title: 'Mobile App Development',
      line: 'Android & iOS products with polished UX, solid backends, and store-ready delivery your customers love using.',
      href: '/mobile-apps',
      image: '/showcase/mobile-phones-fan.webp',
    },
    {
      id: 'seo',
      title: 'SEO & Paid Ads',
      line: 'Search, answer engines, generative visibility, and paid media — so the right customers find you and convert.',
      href: '/seo-ppc',
      image: '/showcase/growth-charts-blue.png',
    },
    {
      id: 'ai',
      title: 'Gen AI Integration',
      line: 'Copilots, automation, and AI systems wired into your workflows — practical, secure, and built for real ops.',
      href: '/custom-software#automation',
      image: '/showcase/ai-chatbot-laptop.png',
    },
    {
      id: 'design',
      title: 'Graphic Design & Figma',
      line: 'Brand systems, UI kits, and production-ready Figma / Stitch files that keep product and marketing aligned.',
      href: '/website-designing#ux',
      image: '/showcase/ux-figma-system.png',
    },
    {
      id: 'software',
      title: 'Custom Software',
      line: 'APIs, platforms, and internal tools engineered around your process — not a one-size template.',
      href: '/custom-software',
      image: '/showcase/web-dashboard-product.webp',
    },
    {
      id: 'ecommerce',
      title: 'E-commerce Solutions',
      line: 'Shopify and custom storefronts built to sell — fast checkout, clear merchandising, and growth-ready foundations.',
      href: '/website-designing',
      image: '/showcase/web-shopify-mac.png',
    },
    {
      id: 'fullstack',
      title: 'Full Stack Applications',
      line: 'End-to-end product builds — frontend, backend, data, and launch — with ownership from blueprint to scale.',
      href: '/custom-software',
      image: '/showcase/hero-devices-product.webp',
    },
  ],
}

/**
 * OUR SOLUTIONS — industry solution cards (above Google reviews).
 * Light grid with dark hover highlight.
 */
export const OUR_SOLUTIONS = {
  title: 'Our Solutions',
  line: 'Custom websites, mobile apps, and digital platforms built for the industries we know best — visually sharp, seamless to use, and designed to grow engagement wherever your customers are.',
  items: [
    {
      id: 'bfsi',
      title: 'BFSI',
      line: 'Secure, conversion-focused banking and insurance experiences — from advisory sites to client portals that build trust online.',
      href: '/custom-software',
      icon: 'Landmark',
    },
    {
      id: 'crowdfunding',
      title: 'Crowdfunding',
      line: 'Campaign platforms and pitch sites that tell the story clearly, build momentum, and make contributing feel effortless.',
      href: '/website-designing',
      icon: 'Users',
    },
    {
      id: 'dating',
      title: 'Dating',
      line: 'Mobile-first dating products with polished profiles, smart matching UX, and the trust signals users need to stay engaged.',
      href: '/mobile-apps',
      icon: 'Heart',
    },
    {
      id: 'elearning',
      title: 'Elearning',
      line: 'Learning platforms and course websites that keep students focused — clear navigation, progress, and content that feels premium.',
      href: '/custom-software',
      icon: 'GraduationCap',
    },
    {
      id: 'fintech',
      title: 'Fintech',
      line: 'Fintech products and dashboards with crisp UI, reliable workflows, and the clarity money decisions demand.',
      href: '/custom-software',
      icon: 'Cpu',
    },
    {
      id: 'fitness',
      title: 'Fitness App',
      line: 'Workout and wellness apps that feel motivating day one — tracking, plans, and coaching flows people actually stick with.',
      href: '/mobile-apps',
      icon: 'Dumbbell',
    },
    {
      id: 'food',
      title: 'Food Delivery',
      line: 'Ordering and delivery experiences built for speed — menus, carts, and live status that keep hungry customers coming back.',
      href: '/mobile-apps',
      icon: 'Bike',
    },
    {
      id: 'healthcare',
      title: 'Healthcare',
      line: 'Patient-friendly websites and apps for clinics and care brands — clear booking, trusted design, and accessible journeys.',
      href: '/website-designing',
      icon: 'HeartPulse',
    },
  ],
}


