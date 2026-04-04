const STEPS = ['Your info', 'Coverage', 'Your quote', 'Account', 'Purchase']

interface StepIndicatorProps {
  current: number  // 1-based
}

export default function StepIndicator({ current }: StepIndicatorProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0, marginBottom: '2rem' }}>
      {STEPS.map((label, i) => {
        const step = i + 1
        const done = step < current
        const active = step === current
        return (
          <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.3rem' }}>
              <div style={{
                width: '2rem',
                height: '2rem',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.8rem',
                fontWeight: 700,
                background: done ? '#2563eb' : active ? '#2563eb' : '#e2e8f0',
                color: done || active ? '#fff' : '#94a3b8',
              }}>
                {done ? '✓' : step}
              </div>
              <span style={{ fontSize: '0.7rem', color: active ? '#2563eb' : '#94a3b8', fontWeight: active ? 600 : 400, whiteSpace: 'nowrap' }}>
                {label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ width: '3rem', height: '2px', background: done ? '#2563eb' : '#e2e8f0', margin: '0 0.25rem', marginBottom: '1.1rem' }} />
            )}
          </div>
        )
      })}
    </div>
  )
}
