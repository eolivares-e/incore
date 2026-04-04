import Link from 'next/link'

interface PaginationProps {
  page: number
  pages: number
  // Server variant: build href from page number
  hrefBuilder?: (page: number) => string
  // Client variant: callback
  onPageChange?: (page: number) => void
}

export default function Pagination({ page, pages, hrefBuilder, onPageChange }: PaginationProps) {
  if (pages <= 1) return null

  const btnStyle = (disabled: boolean): React.CSSProperties => ({
    padding: '0.4rem 0.85rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    background: disabled ? '#f1f5f9' : '#fff',
    color: disabled ? '#94a3b8' : '#374151',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: '0.875rem',
    textDecoration: 'none',
    display: 'inline-block',
  })

  const prevPage = page - 1
  const nextPage = page + 1

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem' }}>
      {hrefBuilder ? (
        <>
          {page > 1 ? (
            <Link href={hrefBuilder(prevPage)} style={btnStyle(false)}>← Prev</Link>
          ) : (
            <span style={btnStyle(true)}>← Prev</span>
          )}
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Page {page} of {pages}</span>
          {page < pages ? (
            <Link href={hrefBuilder(nextPage)} style={btnStyle(false)}>Next →</Link>
          ) : (
            <span style={btnStyle(true)}>Next →</span>
          )}
        </>
      ) : (
        <>
          <button
            onClick={() => onPageChange?.(prevPage)}
            disabled={page <= 1}
            style={btnStyle(page <= 1)}
          >
            ← Prev
          </button>
          <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Page {page} of {pages}</span>
          <button
            onClick={() => onPageChange?.(nextPage)}
            disabled={page >= pages}
            style={btnStyle(page >= pages)}
          >
            Next →
          </button>
        </>
      )}
    </div>
  )
}
