import RevampHeader from '../components/revamp/RevampHeader'
import SiteFooter from '../components/SiteFooter'
import SeoHead from '../components/SeoHead'
import { SITE_CONTACT } from '../data/revampContent'
import './legal-page.css'

const SECTIONS = [
  {
    title: 'Who we are',
    body: [
      `Our website address is https://zeorbit.com. ZeOrbit is a U.S. digital agency based in San Diego, California (${SITE_CONTACT.address.line1}, ${SITE_CONTACT.address.line2}).`,
      `You can reach us at ${SITE_CONTACT.email} or ${SITE_CONTACT.phone}.`,
    ],
  },
  {
    title: 'What personal data we collect',
    body: [
      'When you use our contact forms, chat, quote requests, or email us, we may collect your name, email address, phone number, company name, project details, and any message you choose to share.',
      'Like most websites, we may also collect technical information such as IP address, browser type, device information, pages visited, and approximate location — used for security, spam prevention, and improving the site.',
    ],
  },
  {
    title: 'Why we collect it',
    body: [
      'We use this information to respond to inquiries, provide website, app, SEO, and software services, improve our products and pages, prevent spam and abuse, and meet legal or contractual obligations.',
      'We do not sell your personal information.',
    ],
  },
  {
    title: 'Cookies and analytics',
    body: [
      'We may use cookies and similar technologies to keep the site working, remember preferences, and understand how visitors use zeorbit.com (for example traffic and page performance).',
      'You can control cookies through your browser settings. Disabling some cookies may affect how parts of the site work.',
    ],
  },
  {
    title: 'Embedded content and third parties',
    body: [
      'Pages may include embedded content (such as maps, videos, or forms). Embedded content from other websites may collect data about you in the same way as if you visited those sites directly.',
      'We may use trusted service providers for hosting, email delivery, analytics, advertising measurement, or customer communication. They process data only as needed to provide those services.',
    ],
  },
  {
    title: 'How long we keep data',
    body: [
      'We keep inquiry and project-related information for as long as needed to respond, deliver services, maintain business records, or meet legal requirements. Technical logs are retained for a shorter period unless needed for security investigations.',
    ],
  },
  {
    title: 'Your rights',
    body: [
      'Depending on where you live, you may have rights to request access to, correction of, or deletion of personal information we hold about you, or to opt out of certain processing.',
      `To make a request, email ${SITE_CONTACT.email} with the subject line “Privacy request.” We may need to verify your identity before fulfilling the request.`,
    ],
  },
  {
    title: 'Children’s privacy',
    body: [
      'Our services are directed to businesses and adults. We do not knowingly collect personal information from children under 13. If you believe a child has provided us information, contact us and we will take appropriate steps to remove it.',
    ],
  },
  {
    title: 'Updates to this policy',
    body: [
      'We may update this Privacy Policy from time to time. The “Last updated” date at the top of this page will change when we do. Continued use of the site after updates means you acknowledge the revised policy.',
    ],
  },
  {
    title: 'Contact',
    body: [
      `Questions about this Privacy Policy? Email ${SITE_CONTACT.email}, call ${SITE_CONTACT.phone}, or write to ZeOrbit, ${SITE_CONTACT.address.line1}, ${SITE_CONTACT.address.line2}.`,
    ],
  },
]

export default function PrivacyPolicyPage() {
  return (
    <div className="cz-page zo-legal-page">
      <SeoHead
        title="Privacy Policy — ZeOrbit"
        description="How ZeOrbit collects, uses, and protects personal information on zeorbit.com."
        path="/privacy-policy"
      />
      <RevampHeader />
      <main className="zo-legal-main" id="main">
        <div className="rv-shell zo-legal-inner">
          <p className="zo-legal-kicker">Legal</p>
          <h1>Privacy Policy</h1>
          <p className="zo-legal-updated">Last updated: August 25, 2026</p>
          <p className="zo-legal-lead">
            This Privacy Policy explains how ZeOrbit (“we,” “us,” or “our”) collects and uses information when you
            visit zeorbit.com or contact us about websites, apps, SEO, or custom software.
          </p>
          {SECTIONS.map((section) => (
            <section key={section.title} className="zo-legal-section">
              <h2>{section.title}</h2>
              {section.body.map((para) => (
                <p key={para.slice(0, 48)}>{para}</p>
              ))}
            </section>
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
