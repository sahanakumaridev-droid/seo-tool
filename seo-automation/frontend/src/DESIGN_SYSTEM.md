# ZEORBIT Design System

One unified **dark** design language across the public landing page and the authenticated app. The single source of truth is [`src/index.css`](./index.css) (tokens + component classes) and the reusable primitives in [`src/components/ui/`](./components/ui).

## Architecture

`index.css` uses CSS cascade layers so Tailwind utilities always win:

```
@layer base        → resets, html/body, headings, scrollbar
@layer components  → .card .btn .badge .alert .modal .data-table nav …
(Tailwind utilities live in a later layer → p-5, mb-2, gap-4, grid always override)
```

> ⚠️ Never add an **unlayered** `* { margin:0; padding:0 }` reset — it silently overrides every Tailwind spacing utility. Tailwind Preflight already resets margins inside `@layer base`.

## Color tokens (CSS variables)

| Token | Value | Use |
|---|---|---|
| `--bg-base` | `#0B0F1A` | app / page background |
| `--bg-surface` | `#111827` | cards, panels |
| `--bg-raised` | `#1A2235` | inputs, hover, rows |
| `--bg-overlay` | `#1E2940` | dropdowns, modals |
| `--border` / `--border-bright` | `#1E2D42` / `#2A3B57` | dividers, field borders |
| `--brand` / `--brand-dark` | `#3B82F6` / `#2563EB` | primary actions |
| `--brand-violet` | `#60A5FA` | accents/links on dark |
| `--green` `--amber` `--red` | `#34D399` `#FBBF24` `#F87171` | semantic status (+ `-soft` fills) |
| `--text-1…4` | `#F1F5F9 · #CBD5E1 · #94A3B8 · #64748B` | text hierarchy |

Type scale: `--font-sans` (Inter), `--font-display` (Sora). Radii: `--radius-sm 8` / `--radius 12` / `--radius-lg 16`. Shadows: `--shadow-sm/md/lg`.

## Reusable components

```jsx
import { Button, Card, CardHeader, Badge, Alert, Field, Input, Textarea, Select, Modal, PageHeader } from '../components/ui'

<PageHeader title="Dashboard" subtitle="Welcome back" actions={<Button icon={Plus}>New</Button>} />

<Button variant="primary|secondary|ghost|danger" size="sm|md|lg" icon={Icon} loading />

<Card hover pad={20}> … </Card>
<Card><CardHeader title="Traffic" subtitle="8 months" icon={BarChart2} /> … </Card>

<Badge tone="brand|success|warning|danger|neutral">Live</Badge>

<Alert variant="info|success|warning|error">Saved.</Alert>

<Field label="Website URL" hint="include https://"><Input placeholder="…" /></Field>

<Modal open={open} onClose={close} title="Connect" footer={<Button>Save</Button>}> … </Modal>
```

## Bare CSS classes (for existing/plain markup)

`.card` `.card-hover` · `.btn .btn-primary/.btn-secondary/.btn-ghost/.btn-danger` · `.badge .badge-up/.badge-down` · `.alert .alert-info/success/warning/error` · `.data-table` · `.tab-active/.tab-inactive` · `.nav-active/.nav-inactive` · `.section-label` · `.gradient-text` · `.modal-overlay .modal`.

Inputs/selects/textareas are styled globally — no class needed.

## Responsive

- `< 900px` — sidebar becomes a slide-in drawer toggled by the Topbar hamburger (`.mobile-only`); a backdrop closes it.
- `.hide-mobile` hides an element below 900px; `.mobile-only` shows it only below 900px.
- All page grids use Tailwind responsive prefixes (`lg:grid-cols-*`) so they collapse to one column on small screens.

## Adoption

New code should use the `components/ui` primitives. Existing pages already share the same look because they consume the global `.card/.btn/.data-table/...` classes and tokens; migrate them to the primitives opportunistically when touched.
