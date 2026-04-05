'use client'

import { useEffect, useState, useRef } from 'react'
import type { User, UserRole } from '@/types'
import { listUsers } from '@/lib/api'
import Table from '@/components/Table'
import Pagination from '@/components/Pagination'
import UserRow from './_components/UserRow'
import UserFormModal from './_components/UserFormModal'

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [page, setPage] = useState(1)
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [activeFilter, setActiveFilter] = useState<'' | 'true' | 'false'>('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modalUser, setModalUser] = useState<User | null | 'new'>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  async function fetchUsers(p: number, s: string) {
    setLoading(true)
    setError('')
    try {
      const params: Parameters<typeof listUsers>[0] = { page: p, size: 20 }
      if (roleFilter) params.role = roleFilter as UserRole
      if (activeFilter !== '') params.is_active = activeFilter === 'true'
      if (s) params.search = s
      const data = await listUsers(params)
      setUsers(data.items)
      setTotal(data.total)
      setPages(data.pages)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers(page, search)
  }, [page, roleFilter, activeFilter]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSearchChange(value: string) {
    setSearch(value)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setPage(1)
      fetchUsers(1, value)
    }, 300)
  }

  function handleUpdate(updated: User) {
    setUsers(prev => prev.map(u => u.id === updated.id ? updated : u))
  }

  function handleDeleted(id: string) {
    setUsers(prev => prev.filter(u => u.id !== id))
    setTotal(prev => prev - 1)
  }

  function handleModalSuccess() {
    setModalUser(null)
    fetchUsers(page, search)
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Users</h1>
        <button
          onClick={() => setModalUser('new')}
          style={{
            padding: '0.5rem 1rem',
            background: '#1e293b',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '0.875rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          + New user
        </button>
      </div>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>{total} total</p>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search by name or email…"
          value={search}
          onChange={e => handleSearchChange(e.target.value)}
          style={{ ...selectStyle, minWidth: '220px' }}
        />
        <select value={roleFilter} onChange={e => { setRoleFilter(e.target.value as UserRole | ''); setPage(1) }} style={selectStyle}>
          <option value="">All roles</option>
          <option value="admin">Admin</option>
          <option value="underwriter">Underwriter</option>
          <option value="agent">Agent</option>
          <option value="customer">Customer</option>
        </select>
        <select value={activeFilter} onChange={e => { setActiveFilter(e.target.value as '' | 'true' | 'false'); setPage(1) }} style={selectStyle}>
          <option value="">All statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', opacity: loading ? 0.6 : 1 }}>
        <Table headers={['Name', 'Email', 'Role', 'Status', 'Superuser', 'Created', 'Actions']}>
          {users.map((u, i) => (
            <UserRow
              key={u.id}
              user={u}
              striped={i % 2 === 1}
              onUpdate={handleUpdate}
              onEdit={user => setModalUser(user)}
              onDeleted={handleDeleted}
            />
          ))}
        </Table>
      </div>

      <Pagination page={page} pages={pages} onPageChange={setPage} />

      {modalUser !== null && (
        <UserFormModal
          user={modalUser === 'new' ? undefined : modalUser}
          onSuccess={handleModalSuccess}
          onClose={() => setModalUser(null)}
        />
      )}
    </div>
  )
}
