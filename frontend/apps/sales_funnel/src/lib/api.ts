import { getAccessToken } from '@/lib/auth'
import type {
  TokenResponse,
  UserResponse,
  PersonalInfo,
  PolicyHolderResponse,
  QuoteResponse,
  AcceptQuoteResponse,
} from '@/types'

const API_BASE =
  process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const API_V1 = `${API_BASE}/api/v1`

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_V1}${path}`, { ...options, headers })

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      message = body.detail ?? body.error ?? message
    } catch { /* ignore */ }
    throw new Error(message)
  }

  return res.json() as Promise<T>
}

export async function register(
  email: string,
  password: string,
  full_name: string
): Promise<UserResponse> {
  return apiFetch<UserResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name }),
  })
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function getPolicyholderByEmail(email: string): Promise<PolicyHolderResponse | null> {
  try {
    return await apiFetch<PolicyHolderResponse>(`/policyholders/by-email/${encodeURIComponent(email)}`)
  } catch {
    return null
  }
}

export async function createPolicyholder(info: PersonalInfo): Promise<PolicyHolderResponse> {
  // Return existing policyholder if already created (e.g. on retry)
  const existing = await getPolicyholderByEmail(info.email)
  if (existing) return existing

  return apiFetch<PolicyHolderResponse>('/policyholders', {
    method: 'POST',
    body: JSON.stringify({
      first_name: info.first_name,
      last_name: info.last_name,
      date_of_birth: info.date_of_birth,
      gender: info.gender,
      email: info.email,
      phone: info.phone,
      street_address: info.street_address,
      city: info.city,
      state: info.state,
      zip_code: info.zip_code,
      country: info.country || 'USA',
      identification_type: info.identification_type,
      identification_number: info.identification_number,
    }),
  })
}

export async function createQuote(
  policy_holder_id: string,
  coverage_amount: number
): Promise<QuoteResponse> {
  return apiFetch<QuoteResponse>('/quotes', {
    method: 'POST',
    body: JSON.stringify({
      policy_holder_id,
      policy_type: 'auto',
      requested_coverage_amount: coverage_amount,
    }),
  })
}

export async function acceptQuote(
  quote_id: string,
  start_date: string,
  end_date: string
): Promise<AcceptQuoteResponse> {
  return apiFetch<AcceptQuoteResponse>(`/quotes/${quote_id}/accept`, {
    method: 'POST',
    body: JSON.stringify({ start_date, end_date }),
  })
}
