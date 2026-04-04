import { cookies } from 'next/headers'
import Table, { Tr, Td } from '@/components/Table'
import Badge from '@/components/Badge'
import { getOverdueInvoices } from '@/lib/api'

export default async function BillingPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get('admin_token')?.value ?? ''

  let invoices = null
  let error = ''
  try {
    invoices = await getOverdueInvoices({ page: 1, page_size: 100 }, token)
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed to load invoices'
  }

  function formatCurrency(amount: number) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
  }

  return (
    <div>
      <h1 style={{ margin: '0 0 0.25rem', fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Overdue Invoices</h1>
      <p style={{ margin: '0 0 1.5rem', color: '#64748b', fontSize: '0.9rem' }}>
        Invoices past their due date
        {invoices ? ` — ${invoices.length} total` : ''}
      </p>

      {error && (
        <div style={{ padding: '1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', color: '#dc2626', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
        <Table headers={['Invoice #', 'Policy ID', 'Amount Due', 'Amount Paid', 'Due Date', 'Status']}>
          {invoices?.map((inv, i) => (
            <Tr key={inv.id} striped={i % 2 === 1}>
              <Td><code style={{ fontSize: '0.8rem' }}>{inv.invoice_number}</code></Td>
              <Td><code style={{ fontSize: '0.75rem', color: '#64748b' }}>{inv.policy_id.slice(0, 8)}…</code></Td>
              <Td><strong style={{ color: '#dc2626' }}>{formatCurrency(inv.amount_due)}</strong></Td>
              <Td>{formatCurrency(inv.amount_paid)}</Td>
              <Td>{new Date(inv.due_date).toLocaleDateString()}</Td>
              <Td><Badge value={inv.status} /></Td>
            </Tr>
          ))}
        </Table>
      </div>
    </div>
  )
}
