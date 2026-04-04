import { cookies } from 'next/headers'
import StatCard from '@/components/StatCard'
import { listUsers, listPolicyholders, listPolicies, getPendingUnderwritingReviews, getOverdueInvoices } from '@/lib/api'

export default async function DashboardPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get('admin_token')?.value ?? ''

  const [users, holders, policies, underwriting, overdue] = await Promise.allSettled([
    listUsers({ page: 1, size: 1 }, token),
    listPolicyholders({ page: 1, page_size: 1 }, token),
    listPolicies({ page: 1, page_size: 1 }, token),
    getPendingUnderwritingReviews({ page: 1, size: 1 }, token),
    getOverdueInvoices({ page: 1, page_size: 100 }, token),
  ])

  const userCount = users.status === 'fulfilled' ? users.value.total : '—'
  const holderCount = holders.status === 'fulfilled' ? holders.value.total : '—'
  const policyCount = policies.status === 'fulfilled' ? policies.value.total : '—'
  const pendingReviews = underwriting.status === 'fulfilled' ? underwriting.value.total : '—'
  const overdueCount = overdue.status === 'fulfilled' ? overdue.value.length : '—'

  return (
    <div>
      <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Dashboard</h1>
      <p style={{ margin: '0 0 2rem', color: '#64748b', fontSize: '0.9rem' }}>System overview</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem' }}>
        <StatCard label="Total Users" value={userCount} />
        <StatCard label="Policy Holders" value={holderCount} />
        <StatCard label="Policies" value={policyCount} />
        <StatCard label="Pending Reviews" value={pendingReviews} color="#d97706" />
        <StatCard label="Overdue Invoices" value={overdueCount} color="#dc2626" />
      </div>

      <div style={{ marginTop: '2rem', padding: '1rem 1.25rem', background: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <h2 style={{ margin: '0 0 0.5rem', fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>Quick links</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {[
            { href: '/users', label: 'Manage Users' },
            { href: '/pricing-rules', label: 'Pricing Rules' },
            { href: '/underwriting', label: 'Underwriting Queue' },
            { href: '/billing', label: 'Overdue Billing' },
          ].map(link => (
            <a
              key={link.href}
              href={link.href}
              style={{
                padding: '0.4rem 0.85rem',
                background: '#f1f5f9',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                color: '#1e293b',
                textDecoration: 'none',
                fontSize: '0.875rem',
              }}
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
