import client from './client'
import type { Board, BoardDetail, Member, Label } from '@/types'

export const boardsApi = {
  list: () => client.get<Board[]>('/boards'),
  create: (title: string, description?: string) =>
    client.post<Board>('/boards', { title, description }),
  get: (id: string) => client.get<BoardDetail>(`/boards/${id}`),
  update: (id: string, data: { title?: string; description?: string }) =>
    client.put<Board>(`/boards/${id}`, data),
  delete: (id: string) => client.delete(`/boards/${id}`),

  listMembers: (boardId: string) => client.get<Member[]>(`/boards/${boardId}/members`),
  addMember: (boardId: string, email: string, role = 'member') =>
    client.post<Member>(`/boards/${boardId}/members`, { email, role }),
  removeMember: (boardId: string, userId: string) =>
    client.delete(`/boards/${boardId}/members/${userId}`),

  listLabels: (boardId: string) => client.get<Label[]>(`/boards/${boardId}/labels`),
  createLabel: (boardId: string, name: string, color: string) =>
    client.post<Label>(`/boards/${boardId}/labels`, { name, color }),
  updateLabel: (labelId: string, name: string, color: string) =>
    client.put<Label>(`/labels/${labelId}`, { name, color }),
  deleteLabel: (labelId: string) =>
    client.delete(`/labels/${labelId}`),
}
