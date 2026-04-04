const ACCESS_TOKEN_KEY = 'sf_access_token'
const COOKIE_NAME = 'sf_token'

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setToken(accessToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  document.cookie = `${COOKIE_NAME}=${accessToken}; path=/; SameSite=Lax; max-age=1800`
}

export function clearToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  document.cookie = `${COOKIE_NAME}=; path=/; max-age=0`
}
