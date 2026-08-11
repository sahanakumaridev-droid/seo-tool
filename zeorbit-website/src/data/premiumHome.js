/** Cinematic homepage — product-launch storytelling + curated showcase imagery. */

export const HERO = {
  brand: 'ZeOrbit',
  eyebrow: 'San Diego · Nationwide',
  headline: 'Digital Solutions\nThat Drive Results.',
  line: 'Websites, apps, SEO, and design solutions that help ambitious brands stand out, get found, and grow faster across the U.S.',
  primaryCta: 'Get Started',
  primaryHref: '#contact',
  scene: '/videos/hero-agency-poster.jpg',
  sceneAlt: 'ZeOrbit USA web design agency cinematic brand film',
  video: '/videos/hero-agency.mp4',
}

/** Alternating content | image strips right after hero (not an immediate full-bleed film). */
export const SERVICE_STRIPS = [
  {
    id: 'websites',
    num: '01',
    label: 'Web Design',
    title: 'Websites that turn visitors into customers.',
    line: 'Custom WordPress, Shopify, Wix, and Squarespace sites — clear offers, fast load, built to convert.',
    href: '/website-designing',
    cta: 'Explore websites',
    image: '/showcase/pro/web-wide.jpg',
    flip: false,
  },
  {
    id: 'apps',
    num: '02',
    label: 'App Design',
    title: 'Mobile apps ready for real users.',
    line: 'iOS and Android products with clean UX, solid backends, and store-ready delivery.',
    href: '/mobile-apps',
    cta: 'Explore apps',
    image: '/showcase/pro/ux-app-prototype.jpg',
    flip: true,
  },
  {
    id: 'seo',
    num: '03',
    label: 'SEO & Ads',
    title: 'SEO that gets you found.',
    line: 'Technical SEO, local visibility, and paid campaigns that bring qualified demand — not vanity traffic.',
    href: '/seo-ppc',
    cta: 'Explore SEO',
    image: '/showcase/growth-dashboard-b.png',
    flip: false,
  },
  {
    id: 'branding',
    num: '04',
    label: 'Graphic Design',
    title: 'Identity that moves people.',
    line: 'Visual systems and creative direction that make your brand unmistakable on every screen.',
    href: '/website-designing#ux',
    cta: 'Explore branding',
    image: '/showcase/pro/graphic-wide-4.jpg',
    flip: true,
  },
]

/** Studio 3–style full-bleed story panels — used mid-page, never right after hero. */
export const FILM_PANELS = {
  afterWork: {
    id: 'craft',
    label: 'Website Design',
    title: 'Designed to convert.\nBuilt to last.',
    line: 'Premium WordPress, Shopify, and custom websites for brands that need to look sharp and sell.',
    href: '/website-designing',
    cta: 'See website craft',
    mediaType: 'video',
    media: '/videos/section-animation.mp4',
    poster: '/videos/section-website-poster.jpg',
  },
  beforeReviews: {
    id: 'growth',
    label: 'Digital Marketing',
    title: 'Get found.\nGet chosen.',
    line: 'SEO, ads, and local growth strategies that put the right customers in front of your business.',
    href: '/seo-ppc',
    cta: 'Explore growth',
    mediaType: 'image',
    media: '/showcase/growth-dashboard-b.png',
    poster: '/showcase/growth-dashboard-b.png',
  },
}

export const INDUSTRIES = {
  kicker: 'Industries We Serve',
  title: 'We understand your industry — and how to grow it.',
  line: 'Focused on digital growth and consumer engagement — helping U.S. brands transform how they show up online.',
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
  headline: 'San Diego based.\nNationwide reach.',
  line: 'ZeOrbit builds websites, apps, and growth systems for ambitious brands across the United States — with hands-on strategy from first sketch to launch.',
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
      image: '/showcase/hero-mac-ipad-product.webp',
      alt: 'Premium website shown on MacBook and iPad',
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
      title: 'Ecommerce - stores',
      meta: 'Shopify · WooCommerce · Payments',
      copy: 'Ecommerce experiences that make browsing effortless — collections, product pages, and checkout flows designed to turn visitors into paying customers.',
      result: 'Built to convert on every device',
      image: '/showcase/pro/commerce-ui-a.jpg',
      alt: 'Professional ecommerce store checkout and payments system',
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
      image: '/showcase/growth-systems-04.webp',
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
