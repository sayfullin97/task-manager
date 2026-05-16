export interface User {
  id: string
  email: string
  name: string
  avatar_url: string | null
  is_admin?: boolean
}

export interface Label {
  id: string
  name: string
  color: string
}

export interface Member {
  user: User
  role: string
}

export interface CardBrief {
  id: string
  column_id: string
  title: string
  position: number
  due_date: string | null
  cover_color: string | null
  assignees: User[]
  labels: Label[]
}

export interface Column {
  id: string
  title: string
  position: number
  cards: CardBrief[]
}

export interface Board {
  id: string
  title: string
  description: string | null
  owner_id: string
  role?: string
}

export interface BoardDetail extends Board {
  columns: Column[]
  members: Member[]
  labels: Label[]
}

export interface Comment {
  id: string
  text: string
  user: User
  created_at: string
}

export interface CardDetail {
  id: string
  column_id: string
  title: string
  description: string | null
  position: number
  due_date: string | null
  cover_color: string | null
  assignees: User[]
  labels: Label[]
  comments: Comment[]
}
