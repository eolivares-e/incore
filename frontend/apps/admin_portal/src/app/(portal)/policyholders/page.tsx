import { cookies } from 'next/headers'
import Table, { Tr, Td } from '@/components/Table'
import Pagination from '@/components/Pagination'
import { listPolicyholders } from '@/lib/api'

const PAGE_SIZE = 20

export default async function PolicyholdersPage({
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
    data = await listPolicyholders({ page, page_size: PAGE_SIZE }, token)
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load policyholders'
  }

  return (
    <div>
      <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Policyholders</h1>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>
        {data ? `${data.total} total` : ''}
      </p>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
        <Table headers={['Name', 'Email', 'Phone', 'City', 'Status', 'Created']}>
          {data?.items.map((h, i) => (
            <Tr key={h.id} striped={i % 2 === 1}>
              <Td>{h.first_name} {h.last_name}</Td>
              <Td>{h.email}</Td>
              <Td>{h.phone}</Td>
              <Td>{h.city}, {h.state}</Td>
              <Td>
                <span style={{
                  padding: '0.2rem 0.6rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: h.is_active ? '#dcfce7' : '#fee2e2',
                  color: h.is_active ? '#166534' : '#991b1b',
                }}>
                  {h.is_active ? 'Active' : 'Inactive'}
                </span>
              </Td>
              <Td>{new Date(h.created_at).toLocaleDateString()}</Td>
            </Tr>
          ))}
        </Table>
      </div>

      {data && (
        <Pagination
          page={page}
          pages={data.pages}
          hrefBuilder={p => `/policyholders?page=${p}`}
        />
      )}
    </div>
  )
}
