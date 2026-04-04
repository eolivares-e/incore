// Auth
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export type UserRole = 'admin' | 'underwriter' | 'agent' | 'customer'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

// Policy Holders
export interface PolicyHolder {
  id: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  email: string
  phone: string
  address_line1: string
  address_line2: string | null
  city: string
  state: string
  postal_code: string
  country: string
  identification_type: string
  identification_number: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Policies
export type PolicyStatus =
  | 'draft'
  | 'pending_approval'
  | 'active'
  | 'suspended'
  | 'expired'
  | 'cancelled'
  | 'pending_renewal'

export type PolicyType = 'auto' | 'home' | 'life' | 'health'

export interface Policy {
  id: string
  policy_number: string
  policyholder_id: string
  policy_type: PolicyType
  status: PolicyStatus
  premium_amount: number
  start_date: string
  end_date: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Quotes
export type QuoteStatus =
  | 'draft'
  | 'pending'
  | 'active'
  | 'accepted'
  | 'rejected'
  | 'expired'
  | 'converted_to_policy'

export type RiskLevel = 'low' | 'medium' | 'high' | 'very_high'

export interface Quote {
  id: string
  quote_number: string
  policy_holder_id: string
  policy_type: PolicyType
  requested_coverage_amount: number
  calculated_premium: number
  risk_level: RiskLevel
  status: QuoteStatus
  valid_until: string
  created_at: string
}

// Pricing Rules
export interface PricingRule {
  id: string
  name: string
  description: string | null
  policy_type: PolicyType
  risk_level: RiskLevel
  base_premium: number
  multiplier_factors: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PricingRuleCreate {
  name: string
  description?: string
  policy_type: PolicyType
  risk_level: RiskLevel
  base_premium: number
  multiplier_factors?: Record<string, unknown>
  is_active?: boolean
}

export interface PricingRuleUpdate {
  name?: string
  description?: string
  base_premium?: number
  multiplier_factors?: Record<string, unknown>
  is_active?: boolean
}

// Underwriting
export type UnderwritingStatus =
  | 'pending'
  | 'in_review'
  | 'approved'
  | 'rejected'
  | 'requires_manual_review'
  | 'conditionally_approved'

export interface UnderwritingReview {
  id: string
  quote_id: string | null
  policy_id: string | null
  reviewer_id: string | null
  status: UnderwritingStatus
  risk_level: RiskLevel
  risk_score: number
  notes: string | null
  approved_at: string | null
  rejected_at: string | null
  created_at: string
}

// Billing
export type InvoiceStatus =
  | 'draft'
  | 'pending'
  | 'sent'
  | 'paid'
  | 'overdue'
  | 'partially_paid'
  | 'cancelled'
  | 'refunded'

export interface Invoice {
  id: string
  invoice_number: string
  policy_id: string
  amount_due: number
  amount_paid: number
  due_date: string
  paid_date: string | null
  status: InvoiceStatus
  created_at: string
}
