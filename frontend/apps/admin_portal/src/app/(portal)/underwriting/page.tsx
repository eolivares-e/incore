import { cookies } from 'next/headers'
import Table, { Tr, Td } from '@/components/Table'
import Badge from '@/components/Badge'
import Pagination from '@/components/Pagination'
import { getPendingUnderwritingReviews } from '@/lib/api'

const PAGE_SIZE = 20

export default async function UnderwritingPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>
}) {
  const cookieStore = await cookies()
  const token = cookieStore.get('admin_token')?.value ?? ''
  const params = await searchParams
  const page = Math.max(1, parseInt(params.page ?? '1', 10))

  let data = null
  let error = ''
  try {
    data = await getPendingUnderwritingReviews({ page, size: PAGE_SIZE }, token)
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load reviews'
  }

  return (
    <div>
      <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Underwriting Queue</h1>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>
        Pending reviews sorted by risk score (highest first)
        {data ? ` — ${data.total} total` : ''}
      </p>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
        <Table headers={['ID', 'Quote / Policy', 'Risk Level', 'Risk Score', 'Status', 'Created']}>
          {data?.items.map((r, i) => (
            <Tr key={r.id} striped={i % 2 === 1}>
              <Td><code style={{ fontSize: '0.75rem', color: '#64748b' }}>{r.id.slice(0, 8)}…</code></Td>
              <Td>
                <span style={{ fontSize: '0.8rem', color: '#475569' }}>
                  {r.quote_id ? `Quote: ${r.quote_id.slice(0, 8)}…` : ''}
                  {r.policy_id ? `Policy: ${r.policy_id.slice(0, 8)}…` : ''}
                </span>
              </Td>
              <Td><Badge value={r.risk_level} /></Td>
              <Td>
                <span style={{
                  fontWeight: 600,
                  color: r.risk_score >= 70 ? '#dc2626' : r.risk_score >= 30 ? '#d97706' : '#16a34a',
                }}>
                  {r.risk_score}
                </span>
              </Td>
              <Td><Badge value={r.status} /></Td>
              <Td>{new Date(r.created_at).toLocaleDateString()}</Td>
            </Tr>
          ))}
        </Table>
      </div>

      {data && (
        <Pagination
          page={page}
          pages={data.pages}
          hrefBuilder={p => `/underwriting?page=${p}`}
        />
      )}
    </div>
  )
}
