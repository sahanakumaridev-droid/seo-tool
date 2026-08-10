/** Cinematic device frames — keynote-grade presentation. */

export function BrowserFrame({ src, alt = '', className = '', large = false, style, ...rest }) {
  return (
    <figure className={`cz-browser ${large ? 'is-large' : ''} ${className}`.trim()} style={style} {...rest}>
      <div className="cz-browser-chrome" aria-hidden="true">
        <i /><i /><i />
        <div className="cz-browser-address" />
      </div>
      <div className="cz-browser-viewport">
        <img src={src} alt={alt} loading="lazy" decoding="async" />
      </div>
    </figure>
  )
}

export function MacBook({ src, alt = '', className = '', style, ...rest }) {
  return (
    <figure className={`cz-mac ${className}`.trim()} style={style} {...rest}>
      <div className="cz-mac-lid">
        <div className="cz-mac-camera" aria-hidden="true" />
        <div className="cz-mac-screen">
          <img src={src} alt={alt} loading="eager" decoding="async" />
        </div>
      </div>
      <div className="cz-mac-base" aria-hidden="true">
        <div className="cz-mac-indent" />
      </div>
    </figure>
  )
}

export function IPhone({ src, alt = '', className = '', style, ...rest }) {
  return (
    <figure className={`cz-iphone ${className}`.trim()} style={style} {...rest}>
      <div className="cz-iphone-frame">
        <div className="cz-iphone-island" aria-hidden="true" />
        <div className="cz-iphone-screen">
          <img src={src} alt={alt} loading="lazy" decoding="async" />
        </div>
      </div>
    </figure>
  )
}

export function Tablet({ src, alt = '', className = '', style, ...rest }) {
  return (
    <figure className={`cz-tablet ${className}`.trim()} style={style} {...rest}>
      <div className="cz-tablet-bezel">
        <img src={src} alt={alt} loading="lazy" decoding="async" />
      </div>
    </figure>
  )
}
