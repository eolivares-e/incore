'use client'

import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Suspense } from 'react'

function ConfirmationContent() {
  const params = useSearchParams()
  const policyNumber = params.get('policy') ?? 'N/A'
  const invoiceNumber = params.get('invoice') ?? 'N/A'
  const amount = parseFloat(params.get('amount') ?? '0')

  const fmt = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      <nav style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '1rem 2rem' }}>
        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#1e293b' }}>InsureCore</span>
      </nav>

      <div style={{ maxWidth: '560px', margin: '4rem auto', padding: '0 1.5rem', textAlign: 'center' }}>
        {/* Success icon */}
        <div style={{ width: '5rem', height: '5rem', borderRadius: '50%', background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2.25rem', margin: '0 auto 1.5rem' }}>
          ✓
        </div>

        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.5rem' }}>
          You're covered!
        </h1>
        <p style={{ color: '#64748b', margin: '0 0 2.5rem', fontSize: '1rem' }}>
          Your auto insurance policy is now active.
        </p>

        {/* Details card */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.5rem', textAlign: 'left', marginBottom: '1.5rem' }}>
          <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '1rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Policy details
          </div>
          {[
            { label: 'Policy number', value: policyNumber },
            { label: 'Annual premium', value: fmt(amount) },
            { label: 'Coverage type', value: 'Auto Insurance' },
          ].map(row => (
            <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #f1f5f9', fontSize: '0.875rem' }}>
              <span style={{ color: '#64748b' }}>{row.label}</span>
              <span style={{ fontWeight: 600, color: '#1e293b' }}>{row.value}</span>
            </div>
          ))}
        </div>

        {/* Next steps */}
        <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '10px', padding: '1.25rem', textAlign: 'left', marginBottom: '2rem' }}>
          <div style={{ fontWeight: 700, color: '#1d4ed8', marginBottom: '0.75rem', fontSize: '0.9rem' }}>What happens next</div>
          {[
            'Your policy is active immediately.',
            `Your annual premium of ${fmt(amount)} will be billed to your account.`,
            "You'll receive policy documents via email.",
            'Contact your agent for any changes or claims.',
          ].map((item, i) => (
            <div key={i} style={{ display: 'flex', gap: '0.5rem', fontSize: '0.875rem', color: '#1e40af', marginBottom: '0.4rem' }}>
              <span>•</span><span>{item}</span>
            </div>
          ))}
        </div>

        <Link href="/" style={{ display: 'inline-block', padding: '0.75rem 2rem', background: '#1e293b', color: '#fff', borderRadius: '8px', textDecoration: 'none', fontWeight: 700, fontSize: '0.9rem' }}>
          Back to home
        </Link>
      </div>
    </div>
  )
}

export default function ConfirmationPage() {
  return (
    <Suspense>
      <ConfirmationContent />
    </Suspense>
  )
}
