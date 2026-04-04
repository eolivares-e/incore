import { ReactNode } from 'react'

interface TableProps {
  headers: string[]
  children: ReactNode
  emptyMessage?: string
}

export default function Table({ headers, children, emptyMessage = 'No records found.' }: TableProps) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
        <thead>
          <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
            {headers.map(h => (
              <th key={h} style={{
                padding: '0.75rem 1rem',
                textAlign: 'left',
                fontWeight: 600,
                color: '#374151',
                whiteSpace: 'nowrap',
              }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {children ?? (
            <tr>
              <td colSpan={headers.length} style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

export function Tr({ children, striped }: { children: ReactNode; striped?: boolean }) {
  return (
    <tr style={{ borderBottom: '1px solid #e2e8f0', background: striped ? '#f8fafc' : '#fff' }}>
      {children}
    </tr>
  )
}

export function Td({ children }: { children: ReactNode }) {
  return (
    <td style={{ padding: '0.75rem 1rem', color: '#374151', verticalAlign: 'middle' }}>
      {children}
    </td>
  )
}
