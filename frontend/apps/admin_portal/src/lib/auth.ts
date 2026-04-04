import type { UserRole } from '@/types'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const COOKIE_NAME = 'admin_token'

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  // Write to cookie for middleware route guard (non-HttpOnly so JS can clear it)
  document.cookie = `${COOKIE_NAME}=${accessToken}; path=/; SameSite=Lax; max-age=1800`
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  document.cookie = `${COOKIE_NAME}=; path=/; max-age=0`
}

interface JwtPayload {
  sub: string
  exp: number
  role?: UserRole
  [key: string]: unknown
}

export function decodeToken(token: string): JwtPayload | null {
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload))
    return decoded as JwtPayload
  } catch {
    return null
  }
}

export function getRole(): UserRole | null {
  const token = getAccessToken()
  if (!token) return null
  const payload = decodeToken(token)
  return payload?.role ?? null
}

export function isAdmin(): boolean {
  return getRole() === 'admin'
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeToken(token)
  if (!payload) return true
  return payload.exp * 1000 < Date.now()
}
