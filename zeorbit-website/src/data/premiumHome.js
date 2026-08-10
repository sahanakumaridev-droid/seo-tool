/** Cinematic homepage — product-launch storytelling + curated showcase imagery. */

export const HERO = {
  brand: 'ZeOrbit',
  headline: 'Digital Solutions\nThat Drive Results.',
  line: 'Websites, apps, SEO, and design solutions that help ambitious brands stand out, get found, and grow faster across the U.S.',
  primaryCta: 'Get Started',
  secondaryCta: 'View Our Work',
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
    image: '/showcase/web-macbook-clean.png',
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
    image: '/showcase/mobile-phones-grid.png',
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
    image: '/showcase/growth-dashboard-a.png',
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
    image: '/showcase/section-fashion.png',
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
    mediaType: 'video',
    media: '/videos/section-agency.mp4',
    poster: '/videos/section-agency-poster.jpg',
  },
}

export const INDUSTRIES = {
  kicker: 'Industries We Serve',
  title: "We're passionate about learning and leveling up.",
  line: 'Focused on digital growth and consumer engagement — helping U.S. brands transform how they show up online.',
  image: '/showcase/ux-desk-tools.png',
  items: [
    { icon: 'UtensilsCrossed', label: 'Food & Beverage' },
    { icon: 'Factory', label: 'Manufacturing' },
    { icon: 'Scale', label: 'Law' },
    { icon: 'Car', label: 'Automotive' },
    { icon: 'MapPin', label: 'Local Commercial' },
    { icon: 'Home', label: 'Real Estate' },
    { icon: 'Dumbbell', label: 'Gym & Fitness' },
    { icon: 'Leaf', label: 'CBD' },
    { icon: 'LineChart', label: 'SaaS & Tech' },
    { icon: 'Scissors', label: 'Beauty' },
    { icon: 'MessagesSquare', label: 'Consultants' },
    { icon: 'CalendarDays', label: 'Event Management' },
    { icon: 'Music', label: 'Artists' },
    { icon: 'Cpu', label: 'IT' },
    { icon: 'Plane', label: 'Tour & Travel' },
    { icon: 'Shield', label: 'Insurance' },
    { icon: 'HeartPulse', label: 'Medical' },
    { icon: 'HardHat', label: 'Construction' },
    { icon: 'GraduationCap', label: 'Education' },
    { icon: 'Smile', label: 'Dental' },
    { icon: 'HandHeart', label: 'Non Profit' },
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
      title: 'Commerce stores',
      meta: 'Shopify · WooCommerce · Payments',
      copy: 'Ecommerce experiences that make browsing effortless — collections, product pages, and checkout flows designed to turn visitors into paying customers.',
      result: 'Built to convert on every device',
      image: '/showcase/web-ecommerce-mac.png',
      alt: 'Ecommerce fashion store on a MacBook',
      href: '/website-designing',
      tone: 'light',
      flip: false,
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
  headline: 'Let’s build\nsomething exceptional.',
  line: 'Tell us about your business and goals. We’ll scope a website, app, or full digital package built around what actually moves the needle for you — then follow up within one business day.',
}
