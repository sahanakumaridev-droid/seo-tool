import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { ArrowRight, CheckCircle2, ChevronDown, Phone } from 'lucide-react'
import RevampHeader from '../components/revamp/RevampHeader'
import ContactForm from '../components/revamp/ContactForm'
import SiteFooter from '../components/SiteFooter'
import { Reveal } from '../components/premium/Reveal'
import { SITE_CONTACT } from '../data/revampContent'
import {
  WDS_FAQS,
  WDS_FINAL_CTA,
  WDS_GROWTH,
  WDS_HERO,
  WDS_PROCESS,
  WDS_PROOF,
  WDS_SERVICES,
  WDS_SUPPORT,
  WDS_WORK,
} from '../data/websiteDesignPage'
import '../components/premium/premium-home.css'
import './website-design-page.css'

function scrollToContact() {
  document.getElementById('wds-contact')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function usePreferMotionVideo() {
  const [preferVideo, setPreferVideo] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: no-preference)')
    const sync = () => setPreferVideo(mq.matches)
    sync()
    mq.addEventListener('change', sync)
    return () => mq.removeEventListener('change', sync)
  }, [])

  return preferVideo
}

function useHashScroll() {
  const { hash, pathname } = useLocation()
  useEffect(() => {
    if (!hash) return undefined
    const id = decodeURIComponent(hash.replace('#', ''))
    let tries = 0
    let timer = 0

    const go = () => {
      const el = document.getElementById(id)
      if (el) {
        el.scrollIntoView({ behavior: 'auto', block: 'start' })
        return
      }
      tries += 1
      if (tries < 16) timer = window.setTimeout(go, 20)
    }

    timer = window.setTimeout(go, 0)
    return () => window.clearTimeout(timer)
  }, [hash, pathname])
}

function FaqItem({ item, open, onToggle }) {
  return (
    <div className={`wds-faq-item${open ? ' is-open' : ''}`}>
      <button type="button" className="wds-faq-q" onClick={onToggle} aria-expanded={open}>
        <span>{item.q}</span>
        <ChevronDown size={18} className="wds-faq-caret" />
      </button>
      {open ? <p className="wds-faq-a">{item.a}</p> : null}
    </div>
  )
}

export default function WebsiteDesignPage() {
  const [openFaq, setOpenFaq] = useState(0)
  const preferVideo = usePreferMotionVideo()
  useHashScroll()

  return (
    <div className="cz-page wds-page" data-hero="pro">
      <RevampHeader />

      {/* PREMIUM SPLIT HERO — copy left, product right */}
      <section className="wds-hero wds-hero-pro" aria-label="Website design">
        <div className="wds-hero-atmosphere" aria-hidden="true">
          <div className="wds-hero-glow" />
          <div className="wds-hero-grain" />
        </div>

        <div className="wds-hero-inner wds-hero-split">
          <div className="wds-hero-copy">
            <p className="wds-hero-eyebrow wds-anim wds-anim-1">{WDS_HERO.eyebrow}</p>
            <h1 className="wds-anim wds-anim-2">{WDS_HERO.title}</h1>
            <p className="wds-hero-lead wds-anim wds-anim-3">{WDS_HERO.lead}</p>
            <div className="wds-hero-cta wds-anim wds-anim-4">
              <button type="button" className="cz-btn-solid" onClick={scrollToContact}>
                Get a free quote
                <ArrowRight size={18} strokeWidth={2.4} />
              </button>
              <a className="wds-hero-ghost" href={`tel:${SITE_CONTACT.phoneTel}`}>
                <Phone size={15} strokeWidth={2.4} />
                Call {SITE_CONTACT.phone}
              </a>
            </div>
          </div>

          <div className="wds-hero-visual wds-anim wds-anim-3" aria-hidden="true">
            {preferVideo && WDS_HERO.video ? (
              <video
                className="wds-hero-device-video"
                src={WDS_HERO.video}
                poster={WDS_HERO.poster || WDS_HERO.image}
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
              />
            ) : (
              <img
                className="wds-hero-device"
                src={WDS_HERO.image}
                alt=""
                width={1200}
                height={900}
                loading="eager"
                decoding="async"
                fetchPriority="high"
              />
            )}
          </div>
        </div>

        <div className="wds-scroll-hint" aria-hidden="true">
          <span />
        </div>
      </section>

      {/* PLATFORM PROOF */}
      <section className="wds-proof" aria-label="Platforms">
        <div className="wds-proof-marquee">
          <div className="wds-proof-track">
            {[...WDS_PROOF, ...WDS_PROOF].map((item, i) => (
              <span key={`${item}-${i}`}>{item}</span>
            ))}
          </div>
        </div>
      </section>

      {/* SERVICES */}
      <section className="wds-section">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">{WDS_SERVICES.kicker}</p>
            <h2>{WDS_SERVICES.title}</h2>
            <p className="cz-whisper">{WDS_SERVICES.lead}</p>
          </Reveal>
          <div className="wds-service-grid">
            {WDS_SERVICES.items.map((item, i) => (
              <Reveal
                key={item.title}
                className="wds-service"
                id={item.id}
                style={{ transitionDelay: `${Math.min(i, 5) * 70}ms` }}
              >
                <button type="button" className="wds-service-btn" onClick={scrollToContact}>
                  <div className="wds-service-media">
                    <img src={item.image} alt="" loading="lazy" decoding="async" />
                  </div>
                  <div className="wds-service-body">
                    <h3>{item.title}</h3>
                    <p>{item.copy}</p>
                    <span>
                      {item.cta} <ArrowRight size={14} strokeWidth={2.2} />
                    </span>
                  </div>
                </button>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* SELECTED WORK */}
      <section className="wds-section wds-section-snow">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">{WDS_WORK.kicker}</p>
            <h2>{WDS_WORK.title}</h2>
            <p className="cz-whisper">{WDS_WORK.lead}</p>
          </Reveal>
          <div className="wds-work-grid">
            {WDS_WORK.items.map((item, i) => (
              <Reveal
                key={item.title}
                className="wds-work-card"
                style={{ transitionDelay: `${i * 90}ms` }}
              >
                {item.href ? (
                  <a
                    className="wds-work-link"
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <div className="wds-work-media">
                      <img src={item.image} alt={item.alt || item.title} loading="lazy" decoding="async" />
                    </div>
                    <div className="wds-work-meta">
                      <h3>{item.title}</h3>
                      <p>{item.meta}</p>
                    </div>
                  </a>
                ) : (
                  <>
                    <div className="wds-work-media">
                      <img src={item.image} alt={item.alt || item.title} loading="lazy" decoding="async" />
                    </div>
                    <div className="wds-work-meta">
                      <h3>{item.title}</h3>
                      <p>{item.meta}</p>
                    </div>
                  </>
                )}
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* PROCESS */}
      <section className="wds-section">
        <div className="cz-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">{WDS_PROCESS.kicker}</p>
            <h2>{WDS_PROCESS.title}</h2>
            <p className="cz-whisper">{WDS_PROCESS.lead}</p>
          </Reveal>
          <ol className="wds-process">
            {WDS_PROCESS.steps.map((step, i) => (
              <Reveal
                as="li"
                key={step.title}
                className="wds-process-step"
                style={{ transitionDelay: `${i * 100}ms` }}
              >
                {step.image ? (
                  <div className="wds-process-media">
                    <img src={step.image} alt="" loading="lazy" decoding="async" />
                  </div>
                ) : null}
                <p className="wds-process-num">{step.num}</p>
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
              </Reveal>
            ))}
          </ol>
        </div>
      </section>

      {/* GROWTH / SEO */}
      <section className="wds-growth">
        <div className="cz-rail wds-growth-grid">
          <Reveal className="wds-growth-copy">
            <p className="cz-kicker is-light">{WDS_GROWTH.kicker}</p>
            <h2>{WDS_GROWTH.title}</h2>
            <p className="wds-growth-lead">{WDS_GROWTH.lead}</p>
            <ul>
              {WDS_GROWTH.points.map((point) => (
                <li key={point}>
                  <CheckCircle2 size={18} strokeWidth={2} />
                  {point}
                </li>
              ))}
            </ul>
            <button type="button" className="cz-btn-solid" onClick={scrollToContact}>
              {WDS_GROWTH.cta}
              <ArrowRight size={18} strokeWidth={2.4} />
            </button>
          </Reveal>
          <Reveal className="wds-growth-media">
            <img src={WDS_GROWTH.image} alt="" loading="lazy" decoding="async" />
          </Reveal>
        </div>
      </section>

      {/* SUPPORT */}
      <section className="wds-section">
        <div className="cz-rail wds-support-grid">
          <Reveal className="wds-support-media">
            <img src={WDS_SUPPORT.image} alt="" loading="lazy" decoding="async" />
          </Reveal>
          <Reveal className="wds-support-copy">
            <p className="cz-kicker">{WDS_SUPPORT.kicker}</p>
            <h2>{WDS_SUPPORT.title}</h2>
            <p className="cz-whisper">{WDS_SUPPORT.lead}</p>
            <ul>
              {WDS_SUPPORT.services.map((s) => (
                <li key={s}>
                  <CheckCircle2 size={17} strokeWidth={2} />
                  {s}
                </li>
              ))}
            </ul>
            <button type="button" className="cz-btn-solid" onClick={scrollToContact}>
              {WDS_SUPPORT.cta}
              <ArrowRight size={18} strokeWidth={2.4} />
            </button>
          </Reveal>
        </div>
      </section>

      {/* FAQ */}
      <section className="wds-section wds-section-snow">
        <div className="cz-rail wds-faq-rail">
          <Reveal className="wds-section-head">
            <p className="cz-kicker">FAQ</p>
            <h2>Questions teams ask before we start.</h2>
          </Reveal>
          <div className="wds-faq-list">
            {WDS_FAQS.map((item, i) => (
              <FaqItem
                key={item.q}
                item={item}
                open={openFaq === i}
                onToggle={() => setOpenFaq(openFaq === i ? -1 : i)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CONTACT */}
      <section id="wds-contact" className="wds-final">
        <div className="cz-rail wds-final-inner">
          <Reveal className="wds-final-copy">
            <p className="wds-final-eyebrow">{WDS_FINAL_CTA.kicker}</p>
            <h2>{WDS_FINAL_CTA.title}</h2>
            <p>{WDS_FINAL_CTA.lead}</p>
            <a className="wds-final-call" href={`tel:${SITE_CONTACT.phoneTel}`}>
              <Phone size={16} strokeWidth={2.2} />
              Prefer to talk? {SITE_CONTACT.phone}
            </a>
          </Reveal>
          <Reveal className="wds-final-form" eager>
            <div className="wds-final-form-head">
              <p>Project inquiry</p>
              <h3>Send a short brief</h3>
            </div>
            <ContactForm hideIntro submitLabel="Get a free quote" />
          </Reveal>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}
