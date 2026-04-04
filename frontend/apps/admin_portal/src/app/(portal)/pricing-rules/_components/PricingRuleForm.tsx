'use client'

import { useState, FormEvent } from 'react'
import type { PricingRule, PolicyType, RiskLevel } from '@/types'
import { createPricingRule, updatePricingRule } from '@/lib/api'

const POLICY_TYPES: PolicyType[] = ['auto', 'home', 'life', 'health']
const RISK_LEVELS: RiskLevel[] = ['low', 'medium', 'high', 'very_high']

interface PricingRuleFormProps {
  rule?: PricingRule
  onSuccess: (rule: PricingRule) => void
  onCancel: () => void
}

export default function PricingRuleForm({ rule, onSuccess, onCancel }: PricingRuleFormProps) {
  const isEdit = !!rule
  const [name, setName] = useState(rule?.name ?? '')
  const [description, setDescription] = useState(rule?.description ?? '')
  const [policyType, setPolicyType] = useState<PolicyType>(rule?.policy_type ?? 'auto')
  const [riskLevel, setRiskLevel] = useState<RiskLevel>(rule?.risk_level ?? 'low')
  const [basePremium, setBasePremium] = useState(String(rule?.base_premium ?? ''))
  const [multiplierFactors, setMultiplierFactors] = useState(
    rule ? JSON.stringify(rule.multiplier_factors, null, 2) : '{}'
  )
  const [isActive, setIsActive] = useState(rule?.is_active ?? true)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')

    let factors: Record<string, unknown>
    try {
      factors = JSON.parse(multiplierFactors)
    } catch {
      setError('Multiplier factors must be valid JSON')
      return
    }

    setLoading(true)
    try {
      let saved: PricingRule
      if (isEdit) {
        saved = await updatePricingRule(rule.id, {
          name,
          description: description || undefined,
          base_premium: parseFloat(basePremium),
          multiplier_factors: factors,
          is_active: isActive,
        })
      } else {
        saved = await createPricingRule({
          name,
          description: description || undefined,
          policy_type: policyType,
          risk_level: riskLevel,
          base_premium: parseFloat(basePremium),
          multiplier_factors: factors,
          is_active: isActive,
        })
      }
      onSuccess(saved)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed')
    } finally {
      setLoading(false)
    }
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '0.875rem',
    boxSizing: 'border-box',
  }
  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '0.3rem',
    fontSize: '0.8rem',
    fontWeight: 600,
    color: '#374151',
  }

  return (
    <div style={{
      background: '#f8fafc',
      border: '1px solid #e2e8f0',
      borderRadius: '8px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
    }}>
      <h3 style={{ margin: '0 0 1.25rem', fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>
        {isEdit ? 'Edit Pricing Rule' : 'New Pricing Rule'}
      </h3>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={labelStyle}>Name *</label>
            <input value={name} onChange={e => setName(e.target.value)} required style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Base Premium ($) *</label>
            <input type="number" value={basePremium} onChange={e => setBasePremium(e.target.value)} required min="0" step="0.01" style={inputStyle} />
          </div>
          <div>
            <label style={labelStyle}>Policy Type *</label>
            <select value={policyType} onChange={e => setPolicyType(e.target.value as PolicyType)} disabled={isEdit} style={inputStyle}>
              {POLICY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label style={labelStyle}>Risk Level *</label>
            <select value={riskLevel} onChange={e => setRiskLevel(e.target.value as RiskLevel)} disabled={isEdit} style={inputStyle}>
              {RISK_LEVELS.map(r => <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>)}
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={labelStyle}>Description</label>
          <input value={description} onChange={e => setDescription(e.target.value)} style={inputStyle} />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={labelStyle}>Multiplier Factors (JSON)</label>
          <textarea
            value={multiplierFactors}
            onChange={e => setMultiplierFactors(e.target.value)}
            rows={4}
            style={{ ...inputStyle, fontFamily: 'monospace', fontSize: '0.8rem', resize: 'vertical' }}
          />
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input type="checkbox" checked={isActive} onChange={e => setIsActive(e.target.checked)} />
            <span style={{ fontSize: '0.875rem', color: '#374151' }}>Active</span>
          </label>
        </div>

        {error && (
          <div style={{ marginBottom: '1rem', padding: '0.6rem 0.75rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button type="submit" disabled={loading} style={{
            padding: '0.5rem 1.25rem',
            background: loading ? '#94a3b8' : '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '0.875rem',
            fontWeight: 600,
          }}>
            {loading ? 'Saving…' : isEdit ? 'Save changes' : 'Create rule'}
          </button>
          <button type="button" onClick={onCancel} style={{
            padding: '0.5rem 1rem',
            background: '#fff',
            color: '#374151',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.875rem',
          }}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
