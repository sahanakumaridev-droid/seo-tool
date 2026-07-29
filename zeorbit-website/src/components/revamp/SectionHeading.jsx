export default function SectionHeading({ eyebrow, title, description }) {
  return (
    <header className="rv-section-heading">
      {eyebrow ? <p className="rv-eyebrow">{eyebrow}</p> : null}
      <h2>{title}</h2>
      {description ? <p className="rv-section-description">{description}</p> : null}
    </header>
  )
}
