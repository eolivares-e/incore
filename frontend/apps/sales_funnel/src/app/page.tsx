import Link from 'next/link'

export default function LandingPage() {
  return (
    <div>
      {/* Nav */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '1rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#1e293b' }}>InsureCore</span>
        <Link href="/get-quote" style={{
          padding: '0.5rem 1.25rem',
          background: '#2563eb',
          color: '#fff',
          borderRadius: '6px',
          textDecoration: 'none',
          fontSize: '0.875rem',
          fontWeight: 600,
        }}>
          Get a Quote
        </Link>
      </nav>

      {/* Hero */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '5rem 2rem 3rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-block', background: '#dbeafe', color: '#1d4ed8', padding: '0.3rem 0.85rem', borderRadius: '9999px', fontSize: '0.8rem', fontWeight: 600, marginBottom: '1.5rem' }}>
          Auto Insurance
        </div>
        <h1 style={{ fontSize: '2.75rem', fontWeight: 800, color: '#0f172a', margin: '0 0 1rem', lineHeight: 1.15 }}>
          Get covered in minutes.<br />No surprises.
        </h1>
        <p style={{ fontSize: '1.15rem', color: '#475569', margin: '0 0 2.5rem', maxWidth: '580px', marginLeft: 'auto', marginRight: 'auto' }}>
          See your personalized auto insurance rate instantly — no account needed. Takes under 2 minutes.
        </p>
        <Link href="/get-quote" style={{
          display: 'inline-block',
          padding: '0.85rem 2.5rem',
          background: '#2563eb',
          color: '#fff',
          borderRadius: '8px',
          textDecoration: 'none',
          fontSize: '1rem',
          fontWeight: 700,
          boxShadow: '0 4px 14px rgba(37,99,235,0.35)',
        }}>
          Get my free quote →
        </Link>
        <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#94a3b8' }}>No credit card required</p>
      </div>

      {/* Features */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '0 2rem 5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem' }}>
        {[
          { icon: '⚡', title: 'Instant quote', body: 'See your price before creating an account.' },
          { icon: '🛡️', title: 'Full coverage', body: 'Liability, collision, and comprehensive options.' },
          { icon: '📄', title: 'Policy in minutes', body: 'Accept your quote and get a policy right away.' },
        ].map(f => (
          <div key={f.title} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.5rem' }}>
            <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{f.icon}</div>
            <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '0.25rem' }}>{f.title}</div>
            <div style={{ fontSize: '0.875rem', color: '#64748b' }}>{f.body}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
