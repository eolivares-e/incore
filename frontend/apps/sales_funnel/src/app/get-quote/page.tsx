'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import StepIndicator from '@/components/StepIndicator'
import PriceBreakdown from '@/components/PriceBreakdown'
import { estimatePremium } from '@/lib/pricing'
import { register, login, createPolicyholder, createQuote, acceptQuote } from '@/lib/api'
import { setToken } from '@/lib/auth'
import type { PersonalInfo, CoverageInfo, PriceEstimate } from '@/types'

// ─── Shared styles ────────────────────────────────────────────────────────────

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.55rem 0.75rem',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  fontSize: '0.9rem',
  boxSizing: 'border-box',
  background: '#fff',
}
const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: '0.3rem',
  fontSize: '0.8rem',
  fontWeight: 600,
  color: '#374151',
}
const primaryBtn: React.CSSProperties = {
  width: '100%',
  padding: '0.75rem',
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: '8px',
  fontSize: '1rem',
  fontWeight: 700,
  cursor: 'pointer',
  marginTop: '1.5rem',
}
const disabledBtn: React.CSSProperties = { ...primaryBtn, background: '#94a3b8', cursor: 'not-allowed' }

// ─── Step 1: Personal info ─────────────────────────────────────────────────────

const GENDERS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
]
const ID_TYPES = [
  { value: 'driver_license', label: "Driver's License" },
  { value: 'passport', label: 'Passport' },
  { value: 'national_id', label: 'National ID' },
  { value: 'ssn', label: 'SSN' },
]

function Step1({
  data,
  onChange,
  onNext,
}: {
  data: Partial<PersonalInfo>
  onChange: (updates: Partial<PersonalInfo>) => void
  onNext: () => void
}) {
  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    onNext()
  }

  const f = (field: keyof PersonalInfo, label: string, type = 'text', required = true) => (
    <div>
      <label style={labelStyle}>{label}{required && ' *'}</label>
      <input
        type={type}
        value={(data[field] as string) ?? ''}
        onChange={e => onChange({ [field]: e.target.value })}
        required={required}
        style={inputStyle}
      />
    </div>
  )

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ margin: '0 0 1.5rem', fontSize: '1.25rem', fontWeight: 700, color: '#1e293b' }}>Tell us about yourself</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {f('first_name', 'First name')}
        {f('last_name', 'Last name')}
        {f('date_of_birth', 'Date of birth', 'date')}
        <div>
          <label style={labelStyle}>Gender *</label>
          <select value={data.gender ?? ''} onChange={e => onChange({ gender: e.target.value as PersonalInfo['gender'] })} required style={inputStyle}>
            <option value="">Select…</option>
            {GENDERS.map(g => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
        {f('email', 'Email', 'email')}
        {f('phone', 'Phone (e.g. +1-555-123-4567)')}
      </div>

      <h3 style={{ margin: '1.5rem 0 1rem', fontSize: '0.95rem', fontWeight: 700, color: '#1e293b' }}>Vehicle (optional)</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {f('vehicle_year', 'Year', 'text', false)}
        {f('vehicle_make', 'Make', 'text', false)}
        {f('vehicle_model', 'Model', 'text', false)}
      </div>

      <h3 style={{ margin: '1.5rem 0 1rem', fontSize: '0.95rem', fontWeight: 700, color: '#1e293b' }}>Address</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ gridColumn: '1 / -1' }}>{f('street_address', 'Street address')}</div>
        {f('city', 'City')}
        {f('state', 'State')}
        {f('zip_code', 'ZIP code')}
        <div>
          <label style={labelStyle}>Country *</label>
          <input type="text" value={data.country ?? 'USA'} onChange={e => onChange({ country: e.target.value })} required style={inputStyle} />
        </div>
      </div>

      <h3 style={{ margin: '1.5rem 0 1rem', fontSize: '0.95rem', fontWeight: 700, color: '#1e293b' }}>Identification</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <label style={labelStyle}>ID type *</label>
          <select value={data.identification_type ?? ''} onChange={e => onChange({ identification_type: e.target.value as PersonalInfo['identification_type'] })} required style={inputStyle}>
            <option value="">Select…</option>
            {ID_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        {f('identification_number', 'ID number')}
      </div>

      <button type="submit" style={primaryBtn}>Continue →</button>
    </form>
  )
}

// ─── Step 2: Coverage ──────────────────────────────────────────────────────────

const COVERAGE_OPTIONS = [
  { value: 50_000, label: '$50,000', desc: 'Basic coverage' },
  { value: 100_000, label: '$100,000', desc: 'Standard' },
  { value: 250_000, label: '$250,000', desc: 'Recommended' },
  { value: 500_000, label: '$500,000', desc: 'Premium' },
]

function Step2({
  data,
  onChange,
  onNext,
  onBack,
}: {
  data: Partial<CoverageInfo>
  onChange: (c: CoverageInfo) => void
  onNext: () => void
  onBack: () => void
}) {
  const selected = data.coverage_amount ?? 100_000

  return (
    <div>
      <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700, color: '#1e293b' }}>Choose your coverage amount</h2>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>This is the maximum your insurer will pay for a covered claim.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {COVERAGE_OPTIONS.map(opt => (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange({ coverage_amount: opt.value })}
            style={{
              padding: '1.25rem',
              border: `2px solid ${selected === opt.value ? '#2563eb' : '#e2e8f0'}`,
              borderRadius: '10px',
              background: selected === opt.value ? '#eff6ff' : '#fff',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#1e293b' }}>{opt.label}</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.2rem' }}>{opt.desc}</div>
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button type="button" onClick={onBack} style={{ flex: 1, padding: '0.75rem', background: '#fff', border: '1px solid #d1d5db', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>
          ← Back
        </button>
        <button type="button" onClick={onNext} style={{ ...primaryBtn, flex: 2, marginTop: 0 }}>
          See my quote →
        </button>
      </div>
    </div>
  )
}

// ─── Step 3: Estimate ──────────────────────────────────────────────────────────

function Step3({
  estimate,
  coverageAmount,
  onNext,
  onBack,
}: {
  estimate: PriceEstimate
  coverageAmount: number
  onNext: () => void
  onBack: () => void
}) {
  return (
    <div>
      <h2 style={{ margin: '0 0 0.25rem', fontSize: '1.25rem', fontWeight: 700, color: '#1e293b' }}>Your quote is ready</h2>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>Create a free account to lock in this rate and activate your policy.</p>

      <PriceBreakdown estimate={estimate} coverageAmount={coverageAmount} />

      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
        <button type="button" onClick={onBack} style={{ flex: 1, padding: '0.75rem', background: '#fff', border: '1px solid #d1d5db', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>
          ← Back
        </button>
        <button type="button" onClick={onNext} style={{ ...primaryBtn, flex: 2, marginTop: 0 }}>
          Get started — create account →
        </button>
      </div>
    </div>
  )
}

// ─── Step 4: Register ──────────────────────────────────────────────────────────

function Step4({
  email,
  onSuccess,
  onBack,
}: {
  email: string
  onSuccess: (token: string) => void
  onBack: () => void
}) {
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [regEmail, setRegEmail] = useState(email)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      try {
        await register(regEmail, password, fullName)
      } catch (err) {
        // If already registered, fall through to login
        const msg = err instanceof Error ? err.message : ''
        if (!msg.toLowerCase().includes('already registered') && !msg.includes('400')) throw err
      }
      const tokens = await login(regEmail, password)
      onSuccess(tokens.access_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700, color: '#1e293b' }}>Create your account</h2>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>Free account to save and activate your policy.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={labelStyle}>Full name *</label>
          <input type="text" value={fullName} onChange={e => setFullName(e.target.value)} required style={inputStyle} />
        </div>
        <div>
          <label style={labelStyle}>Email *</label>
          <input type="email" value={regEmail} onChange={e => setRegEmail(e.target.value)} required style={inputStyle} />
        </div>
        <div>
          <label style={labelStyle}>Password *</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} style={inputStyle} />
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Min 8 characters, must include uppercase, lowercase, and a number</span>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: '1rem', padding: '0.6rem 0.75rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button type="button" onClick={onBack} style={{ flex: 1, padding: '0.75rem', background: '#fff', border: '1px solid #d1d5db', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, marginTop: '1.5rem' }}>
          ← Back
        </button>
        <button type="submit" disabled={loading} style={{ ...(!loading ? primaryBtn : disabledBtn), flex: 2 }}>
          {loading ? 'Creating account…' : 'Create account →'}
        </button>
      </div>
    </form>
  )
}

// ─── Step 5: Review & purchase ─────────────────────────────────────────────────

function Step5({
  personalInfo,
  coverageAmount,
  estimate,
  onBack,
  onSuccess,
}: {
  personalInfo: PersonalInfo
  coverageAmount: number
  estimate: PriceEstimate
  onBack: () => void
  onSuccess: (policyNumber: string, invoiceNumber: string, amount: number) => void
}) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function fmt(n: number) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)
  }

  async function handlePurchase() {
    setError('')
    setLoading(true)
    try {
      // 1. Create policyholder
      const ph = await createPolicyholder(personalInfo)

      // 2. Create quote
      const quote = await createQuote(ph.id, coverageAmount)

      // 3. Accept quote (1-year policy starting today)
      const today = new Date()
      const nextYear = new Date(today)
      nextYear.setFullYear(today.getFullYear() + 1)
      const fmt8601 = (d: Date) => d.toISOString().split('T')[0]

      const result = await acceptQuote(quote.id, fmt8601(today), fmt8601(nextYear))

      const policyNumber = result.policy?.policy_number ?? 'N/A'
      const invoiceNumber = result.invoice?.invoice_number ?? policyNumber
      const invoiceAmount = result.invoice?.amount_due ?? result.policy?.premium_amount ?? estimate.annual_premium

      onSuccess(policyNumber, invoiceNumber, invoiceAmount)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Purchase failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const rowStyle: React.CSSProperties = { display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', padding: '0.4rem 0', borderBottom: '1px solid #f1f5f9' }

  return (
    <div>
      <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.25rem', fontWeight: 700, color: '#1e293b' }}>Review your policy</h2>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>Everything looks good? Confirm to activate your coverage.</p>

      <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1rem' }}>
        <div style={{ fontWeight: 700, color: '#1e293b', marginBottom: '0.75rem', fontSize: '0.9rem' }}>Policy details</div>
        <div style={rowStyle}><span style={{ color: '#64748b' }}>Type</span><span>Auto Insurance</span></div>
        <div style={rowStyle}><span style={{ color: '#64748b' }}>Insured</span><span>{personalInfo.first_name} {personalInfo.last_name}</span></div>
        <div style={rowStyle}><span style={{ color: '#64748b' }}>Coverage</span><span>{fmt(coverageAmount)}</span></div>
        <div style={rowStyle}><span style={{ color: '#64748b' }}>Risk level</span><span style={{ textTransform: 'capitalize' }}>{estimate.risk_level.replace('_', ' ')}</span></div>
        <div style={{ ...rowStyle, borderBottom: 'none', fontWeight: 700 }}><span>Annual premium</span><span style={{ color: '#2563eb' }}>{fmt(estimate.annual_premium)}</span></div>
      </div>

      <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '1rem', fontSize: '0.875rem', color: '#1d4ed8', marginBottom: '1.5rem' }}>
        Your policy starts today. An invoice for {fmt(estimate.annual_premium)} will be generated and due within 30 days.
      </div>

      {error && (
        <div style={{ marginBottom: '1rem', padding: '0.6rem 0.75rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', fontSize: '0.875rem' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button type="button" onClick={onBack} disabled={loading} style={{ flex: 1, padding: '0.75rem', background: '#fff', border: '1px solid #d1d5db', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600 }}>
          ← Back
        </button>
        <button type="button" onClick={handlePurchase} disabled={loading} style={{ ...(loading ? disabledBtn : primaryBtn), flex: 2, marginTop: 0 }}>
          {loading ? 'Activating your policy…' : 'Confirm & activate →'}
        </button>
      </div>
    </div>
  )
}

// ─── Main wizard ───────────────────────────────────────────────────────────────

export default function GetQuotePage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [personalInfo, setPersonalInfo] = useState<Partial<PersonalInfo>>({ country: 'USA' })
  const [coverage, setCoverage] = useState<Partial<CoverageInfo>>({ coverage_amount: 100_000 })
  const [estimate, setEstimate] = useState<PriceEstimate | null>(null)

  function goToEstimate() {
    const est = estimatePremium(
      personalInfo.date_of_birth!,
      coverage.coverage_amount ?? 100_000
    )
    setEstimate(est)
    setStep(3)
  }

  function handleRegistered(token: string) {
    setToken(token)
    setStep(5)
  }

  function handlePurchaseSuccess(policyNumber: string, invoiceNumber: string, amount: number) {
    router.push(
      `/confirmation?policy=${encodeURIComponent(policyNumber)}&invoice=${encodeURIComponent(invoiceNumber)}&amount=${amount}`
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {/* Nav */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #e2e8f0', padding: '1rem 2rem' }}>
        <a href="/" style={{ fontWeight: 700, fontSize: '1.1rem', color: '#1e293b', textDecoration: 'none' }}>InsureCore</a>
      </nav>

      <div style={{ maxWidth: '680px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
        <StepIndicator current={step} />

        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '2rem' }}>
          {step === 1 && (
            <Step1
              data={personalInfo}
              onChange={updates => setPersonalInfo(prev => ({ ...prev, ...updates }))}
              onNext={() => setStep(2)}
            />
          )}
          {step === 2 && (
            <Step2
              data={coverage}
              onChange={c => setCoverage(c)}
              onNext={goToEstimate}
              onBack={() => setStep(1)}
            />
          )}
          {step === 3 && estimate && (
            <Step3
              estimate={estimate}
              coverageAmount={coverage.coverage_amount ?? 100_000}
              onNext={() => setStep(4)}
              onBack={() => setStep(2)}
            />
          )}
          {step === 4 && (
            <Step4
              email={personalInfo.email ?? ''}
              onSuccess={handleRegistered}
              onBack={() => setStep(3)}
            />
          )}
          {step === 5 && estimate && (
            <Step5
              personalInfo={personalInfo as PersonalInfo}
              coverageAmount={coverage.coverage_amount ?? 100_000}
              estimate={estimate}
              onBack={() => setStep(4)}
              onSuccess={handlePurchaseSuccess}
            />
          )}
        </div>
      </div>
    </div>
  )
}
