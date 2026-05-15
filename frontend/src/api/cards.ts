import client from './client'
import type { CardDetail } from '@/types'

export const cardsApi = {
  create: (columnId: string, title: string) =>
    client.post<CardDetail>(`/columns/${columnId}/cards`, { title }),
  get: (id: string) => client.get<CardDetail>(`/cards/${id}`),
  update: (id: string, data: { title?: string; description?: string; due_date?: string; cover_color?: string }) =>
    client.put<CardDetail>(`/cards/${id}`, data),
  delete: (id: string) => client.delete(`/cards/${id}`),
  move: (id: string, columnId: string, position: number) =>
    client.post<CardDetail>(`/cards/${id}/move`, { column_id: columnId, position }),

  addAssignee: (id: string, userId: string) =>
    client.post<CardDetail>(`/cards/${id}/assignees`, { user_id: userId }),
  removeAssignee: (id: string, userId: string) =>
    client.delete(`/cards/${id}/assignees/${userId}`),

  addLabel: (id: string, labelId: string) =>
    client.post<CardDetail>(`/cards/${id}/labels`, { label_id: labelId }),
  removeLabel: (id: string, labelId: string) =>
    client.delete(`/cards/${id}/labels/${labelId}`),

  addComment: (id: string, text: string) =>
    client.post(`/cards/${id}/comments`, { text }),
  updateComment: (commentId: string, text: string) =>
    client.put(`/comments/${commentId}`, { text }),
  deleteComment: (commentId: string) =>
    client.delete(`/comments/${commentId}`),
}
