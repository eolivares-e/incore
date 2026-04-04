'use client'

import { useState } from 'react'
import type { User, UserRole } from '@/types'
import { activateUser, deactivateUser, changeUserRole } from '@/lib/api'
import Badge from '@/components/Badge'
import { Tr, Td } from '@/components/Table'

const ROLES: UserRole[] = ['admin', 'underwriter', 'agent', 'customer']

interface UserRowProps {
  user: User
  striped: boolean
  onUpdate: (updated: User) => void
}

export default function UserRow({ user, striped, onUpdate }: UserRowProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleToggleActive() {
    setLoading(true)
    setError('')
    try {
      const updated = user.is_active ? await deactivateUser(user.id) : await activateUser(user.id)
      onUpdate(updated)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setLoading(false)
    }
  }

  async function handleRoleChange(role: UserRole) {
    if (role === user.role) return
    setLoading(true)
    setError('')
    try {
      const updated = await changeUserRole(user.id, role)
      onUpdate(updated)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Tr striped={striped}>
        <Td>{user.full_name}</Td>
        <Td>{user.email}</Td>
        <Td>
          <select
            value={user.role}
            onChange={e => handleRoleChange(e.target.value as UserRole)}
            disabled={loading || user.is_superuser}
            style={{
              padding: '0.25rem 0.5rem',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              fontSize: '0.8rem',
              cursor: user.is_superuser ? 'not-allowed' : 'pointer',
            }}
          >
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </Td>
        <Td>
          <Badge value={user.is_active ? 'active' : 'cancelled'} />
        </Td>
        <Td>{user.is_superuser ? <Badge value="admin" /> : null}</Td>
        <Td>{new Date(user.created_at).toLocaleDateString()}</Td>
        <Td>
          <button
            onClick={handleToggleActive}
            disabled={loading || user.is_superuser}
            style={{
              padding: '0.25rem 0.6rem',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              background: user.is_active ? '#fef2f2' : '#f0fdf4',
              color: user.is_active ? '#dc2626' : '#16a34a',
              cursor: user.is_superuser ? 'not-allowed' : 'pointer',
              fontSize: '0.8rem',
              fontWeight: 500,
            }}
          >
            {loading ? '…' : user.is_active ? 'Deactivate' : 'Activate'}
          </button>
        </Td>
      </Tr>
      {error && (
        <tr>
          <td colSpan={7} style={{ padding: '0.25rem 1rem', background: '#fef2f2', color: '#dc2626', fontSize: '0.8rem' }}>
            {error}
          </td>
        </tr>
      )}
    </>
  )
}
