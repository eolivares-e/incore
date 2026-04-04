// Auth
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

// Form state
export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'
export type IdentificationType = 'passport' | 'driver_license' | 'national_id' | 'ssn' | 'tax_id' | 'other'

export interface PersonalInfo {
  first_name: string
  last_name: string
  date_of_birth: string   // YYYY-MM-DD
  gender: Gender
  email: string
  phone: string
  street_address: string
  city: string
  state: string
  zip_code: string
  country: string
  identification_type: IdentificationType
  identification_number: string
  // Vehicle info (UI only, not sent to backend)
  vehicle_year: string
  vehicle_make: string
  vehicle_model: string
}

export interface CoverageInfo {
  coverage_amount: number   // in dollars
}

// Pricing
export type RiskLevel = 'low' | 'medium' | 'high' | 'very_high'

export interface PriceEstimate {
  annual_premium: number
  monthly_premium: number
  risk_level: RiskLevel
  risk_score: number
  breakdown: {
    base_premium: number
    coverage_adjustment: number
    age_multiplier: number
    age_reason: string
  }
}

// API responses
export interface PolicyHolderResponse {
  id: string
  first_name: string
  last_name: string
  email: string
}

export interface QuoteResponse {
  id: string
  quote_number: string
  calculated_premium: number
  risk_level: RiskLevel
  status: string
  valid_until: string
}

export interface PolicyResponse {
  id: string
  policy_number: string
  status: string
  premium_amount: number
}

export interface InvoiceResponse {
  id: string
  invoice_number: string
  amount_due: number
  due_date: string
  status: string
}

export interface AcceptQuoteResponse {
  quote: QuoteResponse
  policy: PolicyResponse
  invoice?: InvoiceResponse
}
