const NODES = ['Keywords', 'Content', 'Rankings', 'Competitors', 'AI', 'WordPress', 'Indexing']

export default function HeroOrbit() {
  return (
    <div className="rv-orbit" aria-hidden="true">
      <div className="rv-orbit-core">
        <span>ZeOrbit</span>
      </div>
      {NODES.map((node, index) => (
        <div
          key={node}
          className="rv-orbit-node"
          style={{ '--rv-node-index': index }}
        >
          {node}
        </div>
      ))}
    </div>
  )
}
