import client from './client'

export interface AdminStats {
  users: number
  boards: number
  columns: number
  cards: number
  comments: number
  labels: number
}

export interface AdminUser {
  id: string
  name: string
  email: string
  is_admin: boolean
  created_at: string
  board_count: number
}

export interface AdminBoard {
  id: string
  title: string
  description: string | null
  owner_name: string
  owner_email: string
  member_count: number
  card_count: number
}

export const adminApi = {
  stats: () => client.get<AdminStats>('/admin/stats'),
  users: () => client.get<AdminUser[]>('/admin/users'),
  boards: () => client.get<AdminBoard[]>('/admin/boards'),
  toggleAdmin: (userId: string) => client.patch<AdminUser>(`/admin/users/${userId}/toggle-admin`),
}
