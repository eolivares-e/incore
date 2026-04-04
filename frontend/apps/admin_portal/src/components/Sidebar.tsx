'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { clearTokens, isAdmin } from '@/lib/auth'

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/users', label: 'Users', adminOnly: true },
  { href: '/policyholders', label: 'Policyholders' },
  { href: '/policies', label: 'Policies' },
  { href: '/pricing-rules', label: 'Pricing Rules', adminOnly: true },
  { href: '/underwriting', label: 'Underwriting' },
  { href: '/billing', label: 'Billing' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const admin = isAdmin()

  function handleLogout() {
    clearTokens()
    router.push('/login')
  }

  return (
    <aside style={{
      width: '220px',
      minHeight: '100vh',
      background: '#1e293b',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      <div style={{ padding: '1.5rem 1.25rem 1rem', borderBottom: '1px solid #334155' }}>
        <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>Insurance Admin</div>
        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>Management Portal</div>
      </div>

      <nav style={{ flex: 1, padding: '1rem 0' }}>
        {navItems.map(item => {
          if (item.adminOnly && !admin) return null
          const active = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'block',
                padding: '0.6rem 1.25rem',
                color: active ? '#f1f5f9' : '#94a3b8',
                background: active ? '#334155' : 'transparent',
                textDecoration: 'none',
                fontSize: '0.875rem',
                fontWeight: active ? 600 : 400,
                borderLeft: active ? '3px solid #60a5fa' : '3px solid transparent',
                transition: 'background 0.15s',
              }}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid #334155' }}>
        <button
          onClick={handleLogout}
          style={{
            width: '100%',
            padding: '0.5rem',
            background: 'transparent',
            border: '1px solid #475569',
            borderRadius: '6px',
            color: '#94a3b8',
            cursor: 'pointer',
            fontSize: '0.875rem',
          }}
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}
