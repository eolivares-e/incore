const colorMap: Record<string, { bg: string; color: string }> = {
  // Policy / quote statuses
  active: { bg: '#dcfce7', color: '#166534' },
  approved: { bg: '#dcfce7', color: '#166534' },
  conditionally_approved: { bg: '#d1fae5', color: '#065f46' },
  paid: { bg: '#dcfce7', color: '#166534' },
  completed: { bg: '#dcfce7', color: '#166534' },

  draft: { bg: '#f1f5f9', color: '#475569' },
  pending: { bg: '#fef9c3', color: '#854d0e' },
  pending_approval: { bg: '#fef9c3', color: '#854d0e' },
  pending_renewal: { bg: '#fef9c3', color: '#854d0e' },
  in_review: { bg: '#fef9c3', color: '#854d0e' },
  requires_manual_review: { bg: '#ffedd5', color: '#9a3412' },
  sent: { bg: '#ede9fe', color: '#5b21b6' },
  processing: { bg: '#ede9fe', color: '#5b21b6' },
  converted_to_policy: { bg: '#dbeafe', color: '#1e40af' },
  accepted: { bg: '#dbeafe', color: '#1e40af' },

  cancelled: { bg: '#fee2e2', color: '#991b1b' },
  rejected: { bg: '#fee2e2', color: '#991b1b' },
  failed: { bg: '#fee2e2', color: '#991b1b' },
  suspended: { bg: '#fee2e2', color: '#991b1b' },

  expired: { bg: '#ffedd5', color: '#9a3412' },
  overdue: { bg: '#ffedd5', color: '#9a3412' },
  partially_paid: { bg: '#ffedd5', color: '#9a3412' },
  partially_refunded: { bg: '#ffedd5', color: '#9a3412' },
  refunded: { bg: '#f1f5f9', color: '#475569' },

  // Risk levels
  low: { bg: '#dcfce7', color: '#166534' },
  medium: { bg: '#fef9c3', color: '#854d0e' },
  high: { bg: '#ffedd5', color: '#9a3412' },
  very_high: { bg: '#fee2e2', color: '#991b1b' },

  // Roles
  admin: { bg: '#dbeafe', color: '#1e40af' },
  underwriter: { bg: '#ede9fe', color: '#5b21b6' },
  agent: { bg: '#d1fae5', color: '#065f46' },
  customer: { bg: '#f1f5f9', color: '#475569' },
}

const DEFAULT = { bg: '#f1f5f9', color: '#475569' }

interface BadgeProps {
  value: string
}

export default function Badge({ value }: BadgeProps) {
  const style = colorMap[value] ?? DEFAULT
  return (
    <span style={{
      display: 'inline-block',
      padding: '0.2rem 0.6rem',
      borderRadius: '9999px',
      fontSize: '0.75rem',
      fontWeight: 600,
      background: style.bg,
      color: style.color,
      textTransform: 'capitalize',
      whiteSpace: 'nowrap',
    }}>
      {value.replace(/_/g, ' ')}
    </span>
  )
}
