'use client'

import { useEffect, useState } from 'react'
import type { Policy, PolicyStatus, PolicyType } from '@/types'
import { listPolicies } from '@/lib/api'
import Table, { Tr, Td } from '@/components/Table'
import Badge from '@/components/Badge'
import Pagination from '@/components/Pagination'

const STATUSES: PolicyStatus[] = ['draft', 'pending_approval', 'active', 'suspended', 'expired', 'cancelled', 'pending_renewal']
const TYPES: PolicyType[] = ['auto', 'home', 'life', 'health']

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<PolicyStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<PolicyType | ''>('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function fetchPolicies(p: number) {
    setLoading(true)
    setError('')
    try {
      const params: Parameters<typeof listPolicies>[0] = { page: p, page_size: 20 }
      if (statusFilter) params.status = statusFilter as PolicyStatus
      if (typeFilter) params.policy_type = typeFilter as PolicyType
      if (search) params.search = search
      const data = await listPolicies(params)
      setPolicies(data.items)
      setTotal(data.total)
      setPages(data.pages)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load policies')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchPolicies(page) }, [page, statusFilter, typeFilter]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    fetchPolicies(1)
  }

  function formatCurrency(n: number) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)
  }

  const selectStyle: React.CSSProperties = {
    padding: '0.4rem 0.6rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '0.875rem',
    background: '#fff',
  }

  return (
    <div>
      <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Policies</h1>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>{total} total</p>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value as PolicyStatus | ''); setPage(1) }} style={selectStyle}>
          <option value="">All statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
        </select>
        <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value as PolicyType | ''); setPage(1) }} style={selectStyle}>
          <option value="">All types</option>
          {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search policy number…"
            style={{ ...selectStyle, width: '200px' }}
          />
          <button type="submit" style={{
            padding: '0.4rem 0.75rem',
            background: '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.875rem',
          }}>
            Search
          </button>
        </form>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', opacity: loading ? 0.6 : 1 }}>
        <Table headers={['Policy #', 'Type', 'Status', 'Premium', 'Start Date', 'End Date']}>
          {policies.map((p, i) => (
            <Tr key={p.id} striped={i % 2 === 1}>
              <Td><code style={{ fontSize: '0.8rem' }}>{p.policy_number}</code></Td>
              <Td><Badge value={p.policy_type} /></Td>
              <Td><Badge value={p.status} /></Td>
              <Td>{formatCurrency(p.premium_amount)}</Td>
              <Td>{new Date(p.start_date).toLocaleDateString()}</Td>
              <Td>{new Date(p.end_date).toLocaleDateString()}</Td>
            </Tr>
          ))}
        </Table>
      </div>

      <Pagination page={page} pages={pages} onPageChange={setPage} />
    </div>
  )
}
