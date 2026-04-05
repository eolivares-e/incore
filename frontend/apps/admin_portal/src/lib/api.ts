import { getAccessToken, clearTokens } from '@/lib/auth'
import type {
  TokenResponse,
  User,
  UserRole,
  PaginatedResponse,
  PolicyHolder,
  Policy,
  PolicyStatus,
  PolicyType,
  PricingRule,
  PricingRuleCreate,
  PricingRuleUpdate,
  UnderwritingReview,
  Invoice,
} from '@/types'

// API_URL (no NEXT_PUBLIC_ prefix) is only available server-side — used for server component fetches
// inside Docker where localhost doesn't reach the backend container.
// NEXT_PUBLIC_API_URL is available client-side (browser → host machine).
const API_BASE =
  process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const API_V1 = `${API_BASE}/api/v1`

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const resolvedToken = token ?? getAccessToken()

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (resolvedToken) {
    headers['Authorization'] = `Bearer ${resolvedToken}`
  }

  const res = await fetch(`${API_V1}${path}`, { ...options, headers })

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      clearTokens()
      window.location.href = '/login'
    }
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      message = body.detail ?? body.error ?? message
    } catch {
      // ignore parse error
    }
    throw new Error(message)
  }

  if (res.status === 204) return undefined as T

  return res.json() as Promise<T>
}

// Auth
export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

// Users
// Backend returns: { users: User[], total, page, size } — no `pages` field, items under `users` key
export async function listUsers(params: {
  page?: number
  size?: number
  role?: UserRole
  is_active?: boolean
  search?: string
} = {}, token?: string): Promise<PaginatedResponse<User>> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.size) q.set('size', String(params.size))
  if (params.role) q.set('role', params.role)
  if (params.is_active !== undefined) q.set('is_active', String(params.is_active))
  if (params.search) q.set('search', params.search)
  const qs = q.toString() ? `?${q}` : ''
  const raw = await apiFetch<{ users: User[]; total: number; page: number; size: number }>(
    `/users${qs}`, {}, token
  )
  return {
    items: raw.users,
    total: raw.total,
    page: raw.page,
    pages: Math.ceil(raw.total / raw.size),
  }
}

export async function createUser(data: {
  email: string
  password: string
  full_name: string
  role: UserRole
}): Promise<User> {
  return apiFetch<User>('/users', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateUser(
  id: string,
  data: { full_name?: string; email?: string }
): Promise<User> {
  return apiFetch<User>(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteUser(id: string): Promise<void> {
  return apiFetch<void>(`/users/${id}`, { method: 'DELETE' })
}

export async function activateUser(id: string): Promise<User> {
  return apiFetch<User>(`/users/${id}/activate`, { method: 'PUT' })
}

export async function deactivateUser(id: string): Promise<User> {
  return apiFetch<User>(`/users/${id}/deactivate`, { method: 'PUT' })
}

export async function changeUserRole(id: string, role: UserRole): Promise<User> {
  return apiFetch<User>(`/users/${id}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  })
}

// Policy Holders
// Backend returns: { items, total, page, page_size, total_pages }
export async function listPolicyholders(params: {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
} = {}, token?: string): Promise<PaginatedResponse<PolicyHolder>> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.search) q.set('search', params.search)
  if (params.is_active !== undefined) q.set('is_active', String(params.is_active))
  const qs = q.toString() ? `?${q}` : ''
  const raw = await apiFetch<{
    items: PolicyHolder[]; total: number; page: number; page_size: number; total_pages: number
  }>(`/policyholders${qs}`, {}, token)
  return { items: raw.items, total: raw.total, page: raw.page, pages: raw.total_pages }
}

// Policies
// Backend returns: { items, total, page, page_size, total_pages }
export async function listPolicies(params: {
  page?: number
  page_size?: number
  status?: PolicyStatus
  policy_type?: PolicyType
  search?: string
} = {}, token?: string): Promise<PaginatedResponse<Policy>> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.status) q.set('status', params.status)
  if (params.policy_type) q.set('policy_type', params.policy_type)
  if (params.search) q.set('search', params.search)
  const qs = q.toString() ? `?${q}` : ''
  const raw = await apiFetch<{
    items: Policy[]; total: number; page: number; page_size: number; total_pages: number
  }>(`/policies${qs}`, {}, token)
  return { items: raw.items, total: raw.total, page: raw.page, pages: raw.total_pages }
}

// Pricing Rules — backend returns a plain list, no pagination
export async function listPricingRules(params: {
  policy_type?: PolicyType
  is_active?: boolean
} = {}, token?: string): Promise<PricingRule[]> {
  const q = new URLSearchParams()
  if (params.policy_type) q.set('policy_type', params.policy_type)
  if (params.is_active !== undefined) q.set('is_active', String(params.is_active))
  const qs = q.toString() ? `?${q}` : ''
  return apiFetch<PricingRule[]>(`/pricing-rules${qs}`, {}, token)
}

export async function createPricingRule(data: PricingRuleCreate): Promise<PricingRule> {
  return apiFetch<PricingRule>('/pricing-rules', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updatePricingRule(id: string, data: PricingRuleUpdate): Promise<PricingRule> {
  return apiFetch<PricingRule>(`/pricing-rules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deletePricingRule(id: string): Promise<void> {
  return apiFetch<void>(`/pricing-rules/${id}`, { method: 'DELETE' })
}

// Underwriting
// Backend returns: { reviews: UnderwritingReview[], total, page, size } — items under `reviews` key
export async function getPendingUnderwritingReviews(params: {
  page?: number
  size?: number
} = {}, token?: string): Promise<PaginatedResponse<UnderwritingReview>> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.size) q.set('size', String(params.size))
  const qs = q.toString() ? `?${q}` : ''
  const raw = await apiFetch<{
    reviews: UnderwritingReview[]; total: number; page: number; size: number
  }>(`/underwriting/reviews/pending/all${qs}`, {}, token)
  return {
    items: raw.reviews,
    total: raw.total,
    page: raw.page,
    pages: Math.ceil(raw.total / raw.size),
  }
}

// Billing
// Backend returns: { items: Invoice[], total, skip, limit } — extract items
export async function getOverdueInvoices(params: {
  page?: number
  page_size?: number
} = {}, token?: string): Promise<Invoice[]> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  const qs = q.toString() ? `?${q}` : ''
  const raw = await apiFetch<{ items: Invoice[]; total: number; skip: number; limit: number }>(
    `/billing/invoices/overdue/list${qs}`, {}, token
  )
  return raw.items
}
