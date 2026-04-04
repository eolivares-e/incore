import type { PriceEstimate } from '@/types'

const riskColors = {
  low: { bg: '#dcfce7', color: '#166534', label: 'Low Risk' },
  medium: { bg: '#fef9c3', color: '#854d0e', label: 'Medium Risk' },
  high: { bg: '#ffedd5', color: '#9a3412', label: 'High Risk' },
  very_high: { bg: '#fee2e2', color: '#991b1b', label: 'Very High Risk' },
}

const ageReasonLabel: Record<string, string> = {
  young_driver: 'Young driver surcharge applied',
  senior_driver: 'Senior driver surcharge applied',
  standard: 'Standard age — no surcharge',
}

interface PriceBreakdownProps {
  estimate: PriceEstimate
  coverageAmount: number
}

function fmt(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)
}

export default function PriceBreakdown({ estimate, coverageAmount }: PriceBreakdownProps) {
  const risk = riskColors[estimate.risk_level]
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden' }}>
      {/* Price header */}
      <div style={{ background: '#1e293b', padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.5rem' }}>Your estimated annual premium</div>
        <div style={{ color: '#fff', fontSize: '3rem', fontWeight: 800, lineHeight: 1 }}>
          {fmt(estimate.annual_premium)}
        </div>
        <div style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '0.5rem' }}>
          or {fmt(estimate.monthly_premium)}/month
        </div>
        <div style={{ marginTop: '1rem' }}>
          <span style={{ ...risk, padding: '0.25rem 0.85rem', borderRadius: '9999px', fontSize: '0.8rem', fontWeight: 700 }}>
            {risk.label}
          </span>
        </div>
      </div>

      {/* Breakdown */}
      <div style={{ padding: '1.5rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
          Price breakdown
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {[
            { label: 'Coverage', value: fmt(coverageAmount) },
            { label: 'Base premium', value: fmt(estimate.breakdown.base_premium) },
            { label: 'Coverage adjustment', value: `+${fmt(estimate.breakdown.coverage_adjustment)}` },
            {
              label: 'Age factor',
              value: estimate.breakdown.age_multiplier !== 1
                ? `×${estimate.breakdown.age_multiplier}`
                : 'None',
              note: ageReasonLabel[estimate.breakdown.age_reason],
            },
          ].map(row => (
            <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#374151' }}>
              <span style={{ color: '#64748b' }}>
                {row.label}
                {row.note && <span style={{ display: 'block', fontSize: '0.75rem', color: '#94a3b8' }}>{row.note}</span>}
              </span>
              <span style={{ fontWeight: 500 }}>{row.value}</span>
            </div>
          ))}
          <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.5rem', display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: '#1e293b' }}>
            <span>Annual total</span>
            <span>{fmt(estimate.annual_premium)}</span>
          </div>
        </div>
        <p style={{ margin: '1rem 0 0', fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center' }}>
          Estimate based on the information provided. Final price confirmed at checkout.
        </p>
      </div>
    </div>
  )
}
