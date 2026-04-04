'use client'

import { useEffect, useState } from 'react'
import type { PricingRule, PolicyType } from '@/types'
import { listPricingRules, deletePricingRule } from '@/lib/api'
import { isAdmin } from '@/lib/auth'
import Table, { Tr, Td } from '@/components/Table'
import Badge from '@/components/Badge'
import PricingRuleForm from './_components/PricingRuleForm'

export default function PricingRulesPage() {
  const [rules, setRules] = useState<PricingRule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingRule, setEditingRule] = useState<PricingRule | undefined>()
  const [typeFilter, setTypeFilter] = useState<PolicyType | ''>('')
  const [admin, setAdmin] = useState(false)

  useEffect(() => {
    setAdmin(isAdmin())
  }, [])

  async function fetchRules() {
    setLoading(true)
    setError('')
    try {
      const params: Parameters<typeof listPricingRules>[0] = {}
      if (typeFilter) params.policy_type = typeFilter as PolicyType
      const data = await listPricingRules(params)
      setRules(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load pricing rules')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRules() }, [typeFilter]) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleDelete(rule: PricingRule) {
    if (!confirm(`Delete rule "${rule.name}"? This cannot be undone.`)) return
    try {
      await deletePricingRule(rule.id)
      setRules(prev => prev.filter(r => r.id !== rule.id))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed')
    }
  }

  function handleFormSuccess(saved: PricingRule) {
    if (editingRule) {
      setRules(prev => prev.map(r => r.id === saved.id ? saved : r))
    } else {
      setRules(prev => [...prev, saved])
    }
    setShowForm(false)
    setEditingRule(undefined)
  }

  function handleEdit(rule: PricingRule) {
    setEditingRule(rule)
    setShowForm(true)
  }

  function handleCancel() {
    setShowForm(false)
    setEditingRule(undefined)
  }

  if (!admin) {
    return (
      <div>
        <h1 style={{ margin: '0 0 1rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Pricing Rules</h1>
        <div style={{ padding: '1.5rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#991b1b' }}>
          Access restricted. Only administrators can manage pricing rules.
        </div>
      </div>
    )
  }

  const formatCurrency = (n: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Pricing Rules</h1>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem' }}>{rules.length} rules</p>
        </div>
        {!showForm && (
          <button
            onClick={() => { setEditingRule(undefined); setShowForm(true) }}
            style={{
              padding: '0.5rem 1.25rem',
              background: '#1e293b',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 600,
            }}
          >
            + New Rule
          </button>
        )}
      </div>

      {showForm && (
        <PricingRuleForm
          rule={editingRule}
          onSuccess={handleFormSuccess}
          onCancel={handleCancel}
        />
      )}

      <div style={{ marginBottom: '1rem' }}>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value as PolicyType | '')}
          style={{ padding: '0.4rem 0.6rem', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.875rem', background: '#fff' }}
        >
          <option value="">All policy types</option>
          {(['auto', 'home', 'life', 'health'] as PolicyType[]).map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', opacity: loading ? 0.6 : 1 }}>
        <Table headers={['Name', 'Policy Type', 'Risk Level', 'Base Premium', 'Active', 'Actions']}>
          {rules.map((rule, i) => (
            <Tr key={rule.id} striped={i % 2 === 1}>
              <Td>
                <div style={{ fontWeight: 500 }}>{rule.name}</div>
                {rule.description && <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{rule.description}</div>}
              </Td>
              <Td><Badge value={rule.policy_type} /></Td>
              <Td><Badge value={rule.risk_level} /></Td>
              <Td>{formatCurrency(rule.base_premium)}</Td>
              <Td>
                <span style={{
                  padding: '0.2rem 0.5rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: rule.is_active ? '#dcfce7' : '#f1f5f9',
                  color: rule.is_active ? '#166534' : '#64748b',
                }}>
                  {rule.is_active ? 'Active' : 'Inactive'}
                </span>
              </Td>
              <Td>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => handleEdit(rule)}
                    style={{ padding: '0.25rem 0.6rem', border: '1px solid #d1d5db', borderRadius: '4px', background: '#fff', cursor: 'pointer', fontSize: '0.8rem' }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(rule)}
                    style={{ padding: '0.25rem 0.6rem', border: '1px solid #fecaca', borderRadius: '4px', background: '#fef2f2', color: '#dc2626', cursor: 'pointer', fontSize: '0.8rem' }}
                  >
                    Delete
                  </button>
                </div>
              </Td>
            </Tr>
          ))}
        </Table>
      </div>
    </div>
  )
}
