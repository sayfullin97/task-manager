import client from './client'
import type { Column } from '@/types'

export const columnsApi = {
  create: (boardId: string, title: string) =>
    client.post<Column>(`/boards/${boardId}/columns`, { title }),
  update: (id: string, data: { title?: string; position?: number }) =>
    client.put<Column>(`/columns/${id}`, data),
  delete: (id: string) => client.delete(`/columns/${id}`),
}
