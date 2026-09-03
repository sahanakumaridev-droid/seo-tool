import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 32, fontFamily: 'system-ui', color: '#111' }}>
          <h1 style={{ fontSize: 20 }}>The SEO tool hit a display error</h1>
          <p style={{ color: '#555' }}>{String(this.state.error.message || this.state.error)}</p>
          <button type="button" onClick={() => window.location.reload()}>Reload</button>
        </div>
      )
    }
    return this.props.children
  }
}
