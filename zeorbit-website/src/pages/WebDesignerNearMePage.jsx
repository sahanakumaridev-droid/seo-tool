import { Link } from 'react-router-dom'
import { ArrowRight, MapPin, Phone, Star } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import ContactForm from '../components/revamp/ContactForm'
import PremiumGoogleReviews from '../components/premium/PremiumGoogleReviews'
import { Reveal } from '../components/premium/Reveal'
import { NEAR_ME_FAQS, SITE_URL, ZEO_LOCAL } from '../data/localBusiness'
import { SITE_CONTACT } from '../data/revampContent'
import '../components/premium/premium-home.css'
import './near-me-page.css'

const PAGE_PATH = '/web-designer-near-me'
const PAGE_TITLE = 'Best Web Designer Near Me in San Diego | ZeOrbit'
const PAGE_DESC =
  'Looking for the best web designer near you in San Diego? ZeOrbit has a 5.0 Google rating, 20+ years experience, and builds WordPress, Shopify & custom websites. Call 619-724-9517.'

export default function WebDesignerNearMePage() {
  return (
    <div className="cz-page zo-near-me-page">
      <RevampHeader />

      <section className="zo-near-me-hero" aria-label="Web designer near me">
        <div className="zo-near-me-shell">
          <p className="cz-kicker">San Diego web design · Near you</p>
          <h1>Best web designer near me in San Diego</h1>
          <p className="zo-near-me-lead">
            ZeOrbit is a San Diego web design company trusted by local businesses for WordPress,
            Shopify, website redesigns, mobile apps, and SEO. {ZEO_LOCAL.rating} stars on Google
            ({ZEO_LOCAL.reviewCount} reviews) · 20+ years · projects from $500.
          </p>
          <div className="zo-near-me-actions">
            <Link className="cz-btn-solid" to="/contact#contact">
              Get a free quote
              <ArrowRight size={18} strokeWidth={2.4} />
            </Link>
            <a className="zo-near-me-phone" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              {SITE_CONTACT.phone}
            </a>
          </div>
          <div className="zo-near-me-trust">
            <Star size={16} fill="currentColor" aria-hidden />
            <span>{ZEO_LOCAL.rating} Google rating</span>
            <span aria-hidden>·</span>
            <span>{ZEO_LOCAL.reviewCount}+ Google reviews</span>
            <span aria-hidden>·</span>
            <a href={ZEO_LOCAL.gbpUrl} target="_blank" rel="noopener noreferrer">
              View on Google Maps
            </a>
          </div>
        </div>
      </section>

      <section className="zo-near-me-block" aria-label="Why ZeOrbit for near me searches">
        <div className="zo-near-me-shell">
          <Reveal>
            <h2>Why San Diego businesses choose ZeOrbit</h2>
            <div className="zo-near-me-grid">
              {[
                {
                  title: 'Local + nationwide',
                  body: 'Based in San Diego with in-person meetings when you want them and fast remote delivery when you don’t.',
                },
                {
                  title: 'WordPress, Shopify & custom',
                  body: 'Business websites, ecommerce stores, landing pages, and redesigns — built to convert, not just look good.',
                },
                {
                  title: 'SEO & AI visibility',
                  body: 'We structure sites for Google, Google AI Mode, and Gemini so customers find you for “near me” searches.',
                },
                {
                  title: 'Clear pricing',
                  body: 'Most website projects run $500–$3,000 with honest scopes before we start building.',
                },
              ].map((item) => (
                <article key={item.title} className="zo-near-me-card">
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      <section className="zo-near-me-block zo-near-me-areas" aria-label="Areas served">
        <div className="zo-near-me-shell">
          <Reveal>
            <h2>Web design near you across San Diego County</h2>
            <p className="zo-near-me-sub">
              We serve businesses searching for a web designer near me in:
            </p>
            <ul className="zo-near-me-tags">
              {ZEO_LOCAL.areaServed.slice(0, 8).map((area) => (
                <li key={area.name}>{area.name}</li>
              ))}
            </ul>
            <Link className="zo-near-me-link" to="/areas/san-diego">
              San Diego web design hub
              <ArrowRight size={15} strokeWidth={2.4} aria-hidden />
            </Link>
          </Reveal>
        </div>
      </section>

      <section className="zo-near-me-block" aria-label="How a San Diego web design project works">
        <div className="zo-near-me-shell">
          <h2>How we design a website for a San Diego business</h2>
          <p className="zo-near-me-sub">
            If you searched “best web designer in San Diego” or “web designer near me,” you need a
            process that is local, priced clearly, and built for Google — not a 500-page content mill.
          </p>
          <div className="zo-near-me-grid">
            {[
              {
                title: '1. Scope the job',
                body: 'We confirm your service, city, and goal — leads, bookings, or ecommerce — then recommend WordPress, Shopify, or a custom stack.',
              },
              {
                title: '2. Build the money pages',
                body: 'Homepage, service pages, and one strong San Diego location page with NAP, FAQs, and structured data. Thin street pages are not the strategy.',
              },
              {
                title: '3. Connect the site',
                body: 'Internal links from services and areas into the pages that should rank. Sitemap and indexing requests after publish.',
              },
              {
                title: '4. Earn prominence',
                body: 'Google Business Profile, genuine reviews, and real directory profiles (Yelp, DesignRush, GoodFirms). We do not sell fake links.',
              },
            ].map((item) => (
              <article key={item.title} className="zo-near-me-card">
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="zo-near-me-block" aria-label="What you get">
        <div className="zo-near-me-shell">
          <h2>What a ZeOrbit website includes</h2>
          <p>
            A typical San Diego small-business site includes mobile-first layout, Core Web Vitals
            hygiene, HTTPS, a contact path (form + 619-724-9517), Google Business alignment, and
            copy that answers how much a website costs, which platform to use, and why you are
            local. Ecommerce builds add Shopify collections, checkout, and product SEO. Apps are
            scoped separately for iOS and Android.
          </p>
          <p>
            Related work:{' '}
            <Link to="/website-designing">website design services</Link>,{' '}
            <Link to="/areas/san-diego">San Diego web design hub</Link>,{' '}
            <Link to="/seo-ppc">SEO and Google Ads</Link>,{' '}
            <Link to="/mobile-apps">mobile apps</Link>,{' '}
            <Link to="/custom-software">custom software</Link>,{' '}
            <Link to="/portfolio">portfolio</Link>.
          </p>
          <p>
            Independent profiles:{' '}
            <a href="https://www.designrush.com/agency/profile/zeorbit" rel="noopener noreferrer">DesignRush</a>,{' '}
            <a href="https://www.goodfirms.co/company/zeorbit" rel="noopener noreferrer">GoodFirms</a>,{' '}
            <a href="https://www.yelp.com/biz/zeorbit-san-diego-2" rel="noopener noreferrer">Yelp</a>,{' '}
            <a href="https://www.bbb.org/us/ca/san-diego/profile/web-design/zeorbit-llc-1126-1000089251" rel="noopener noreferrer">BBB</a>,{' '}
            <a href="https://www.linkedin.com/company/zeorbit/" rel="noopener noreferrer">LinkedIn</a>.
          </p>
        </div>
      </section>

      <section className="zo-near-me-block" aria-label="Google reviews">
        <div className="zo-near-me-shell">
          <PremiumGoogleReviews />
        </div>
      </section>

      <section className="zo-near-me-block" aria-label="Contact">
        <div className="zo-near-me-shell zo-near-me-contact">
          <Reveal>
            <h2>Talk with a web designer near you</h2>
            <p className="zo-near-me-sub">
              <MapPin size={16} strokeWidth={2.2} aria-hidden />
              {ZEO_LOCAL.address.streetAddress}, {ZEO_LOCAL.address.addressLocality},{' '}
              {ZEO_LOCAL.address.addressRegion} {ZEO_LOCAL.address.postalCode}
            </p>
            <ContactForm />
          </Reveal>
        </div>
      </section>

      <section className="zo-near-me-block zo-near-me-faq" aria-label="FAQ">
        <div className="zo-near-me-shell">
          <h2>Web designer near me — common questions</h2>
          <div className="zo-near-me-faq-list">
            {NEAR_ME_FAQS.map((item) => (
              <details key={item.q} className="zo-near-me-faq-item">
                <summary>{item.q}</summary>
                <p>{item.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}

export { PAGE_PATH, PAGE_TITLE, PAGE_DESC, SITE_URL }
