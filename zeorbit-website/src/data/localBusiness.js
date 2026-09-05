/** Canonical NAP + schema for Google AI Mode, Gemini, and local search. */
import { SITE_CONTACT } from './revampContent'

export const SITE_URL = 'https://zeorbit.com'

export const ZEO_LOCAL = {
  name: SITE_CONTACT.google.businessName,
  alternateName: 'ZeOrbit',
  url: SITE_URL,
  telephone: SITE_CONTACT.phoneTel,
  email: SITE_CONTACT.email,
  priceRange: '$$',
  geo: {
    latitude: 32.80964,
    longitude: -117.20147,
  },
  address: {
    streetAddress: '4231 Balboa Avenue, Suite 1340',
    addressLocality: 'San Diego',
    addressRegion: 'CA',
    postalCode: '92117',
    addressCountry: 'US',
  },
  mapsUrl: SITE_CONTACT.address.mapsUrl,
  gbpUrl: SITE_CONTACT.google.reviewsUrl,
  placeId: SITE_CONTACT.google.placeId,
  rating: Number(SITE_CONTACT.google.rating),
  reviewCount: SITE_CONTACT.google.reviewCount,
  sameAs: [
    SITE_CONTACT.google.reviewsUrl,
    'https://www.yelp.com/biz/zeorbit-san-diego-2',
    'https://www.bbb.org/us/ca/san-diego/profile/web-design/zeorbit-llc-1126-1000089251',
    'https://www.linkedin.com/company/zeorbit/',
    'https://www.facebook.com/zeorbit.web.designers.mobileapp.developers',
    'https://www.instagram.com/zeorbit/',
    'https://maps.apple/p/VA-_LREgJ5PzDV',
    'https://www.expertise.com/business/web-design/california/san-diego',
    'https://www.designrush.com/agency/profile/zeorbit',
    'https://www.goodfirms.co/company/zeorbit',
  ],
  areaServed: [
    { name: 'San Diego', region: 'CA' },
    { name: 'La Jolla', region: 'CA' },
    { name: 'Chula Vista', region: 'CA' },
    { name: 'Oceanside', region: 'CA' },
    { name: 'Carlsbad', region: 'CA' },
    { name: 'El Cajon', region: 'CA' },
    { name: 'Escondido', region: 'CA' },
    { name: 'Orange County', region: 'CA' },
    { name: 'Los Angeles', region: 'CA' },
    { name: 'California', region: 'US' },
    { name: 'United States', region: 'US' },
  ],
  services: [
    'Website Design',
    'WordPress Development',
    'Shopify Website Design',
    'Website Redesign',
    'Mobile App Development',
    'SEO',
    'Local SEO',
    'Google Ads',
  ],
}

export const NEAR_ME_FAQS = [
  {
    q: 'Who is the best web designer near me in San Diego?',
    a: 'ZeOrbit is a San Diego web design company with a 5.0 Google rating, 1,000+ client reviews, and 20+ years of experience building WordPress, Shopify, and custom websites for local businesses. Call 619-724-9517 or visit zeorbit.com/contact for a free quote.',
  },
  {
    q: 'Does ZeOrbit offer web design near me?',
    a: 'Yes. ZeOrbit serves San Diego County and clients nationwide. We meet locally at our San Diego HQ (4231 Balboa Avenue) and work remotely for businesses across California and the United States.',
  },
  {
    q: 'How much does a website cost with a web designer near me?',
    a: 'ZeOrbit website projects typically start around $500–$3,000 depending on scope — WordPress, Shopify, redesigns, and custom builds. We provide clear quotes before work begins.',
  },
  {
    q: 'What services does ZeOrbit offer besides web design?',
    a: 'ZeOrbit also builds mobile apps (iOS and Android), custom software, SEO, local SEO, Google Ads, and ongoing website care — all from our San Diego team.',
  },
  {
    q: 'How do I contact a web designer near me at ZeOrbit?',
    a: 'Call +1 (619) 724-9517, email info@zeorbit.com, or use the contact form at zeorbit.com/contact. We respond within one business day.',
  },
]

export function buildLocalBusinessSchema({ pageUrl = SITE_URL, description } = {}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    '@id': `${SITE_URL}/#localbusiness`,
    name: ZEO_LOCAL.name,
    alternateName: ZEO_LOCAL.alternateName,
    url: SITE_URL,
    telephone: ZEO_LOCAL.telephone,
    email: ZEO_LOCAL.email,
    priceRange: ZEO_LOCAL.priceRange,
    image: `${SITE_URL}/zeorbit-logo.webp`,
    logo: `${SITE_URL}/zeorbit-logo.webp`,
    description:
      description ||
      'San Diego web design company for WordPress, Shopify, website redesigns, mobile apps, SEO, and Google Ads. 5.0 Google rating. Serving San Diego County and the United States.',
    address: {
      '@type': 'PostalAddress',
      ...ZEO_LOCAL.address,
    },
    geo: {
      '@type': 'GeoCoordinates',
      latitude: ZEO_LOCAL.geo.latitude,
      longitude: ZEO_LOCAL.geo.longitude,
    },
    hasMap: ZEO_LOCAL.mapsUrl,
    areaServed: ZEO_LOCAL.areaServed.map((a) => ({
      '@type': 'Place',
      name: a.name,
      address: { '@type': 'PostalAddress', addressRegion: a.region, addressCountry: 'US' },
    })),
    sameAs: ZEO_LOCAL.sameAs,
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: ZEO_LOCAL.rating,
      reviewCount: ZEO_LOCAL.reviewCount,
      bestRating: 5,
      worstRating: 1,
    },
    knowsAbout: ZEO_LOCAL.services,
    makesOffer: ZEO_LOCAL.services.map((name) => ({
      '@type': 'Offer',
      itemOffered: { '@type': 'Service', name, provider: { '@id': `${SITE_URL}/#localbusiness` } },
    })),
  }
}

export function buildFaqSchema(faqs) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((item) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: { '@type': 'Answer', text: item.a },
    })),
  }
}

export function buildOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${SITE_URL}/#organization`,
    name: ZEO_LOCAL.alternateName,
    legalName: ZEO_LOCAL.name,
    url: SITE_URL,
    logo: `${SITE_URL}/zeorbit-logo.webp`,
    email: ZEO_LOCAL.email,
    telephone: ZEO_LOCAL.telephone,
    address: {
      '@type': 'PostalAddress',
      ...ZEO_LOCAL.address,
    },
    sameAs: ZEO_LOCAL.sameAs,
  }
}
