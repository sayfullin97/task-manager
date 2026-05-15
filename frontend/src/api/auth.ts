import client from './client'
import type { User } from '@/types'

interface TokenResponse {
  access_token: string
  refresh_token: string
  user: User
}

export const authApi = {
  register: (email: string, password: string, name: string) =>
    client.post<TokenResponse>('/auth/register', { email, password, name }),

  login: (email: string, password: string) =>
    client.post<TokenResponse>('/auth/login', { email, password }),

  me: () => client.get<User>('/auth/me'),
}
