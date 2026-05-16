import { defineStore } from 'pinia'
import { ref } from 'vue'
import { boardsApi } from '@/api/boards'
import { columnsApi } from '@/api/columns'
import { cardsApi } from '@/api/cards'
import type { Board, BoardDetail, CardDetail } from '@/types'

export const useBoardsStore = defineStore('boards', () => {
  const boards = ref<Board[]>([])
  const currentBoard = ref<BoardDetail | null>(null)
  const activeCard = ref<CardDetail | null>(null)
  const loading = ref(false)
  const boardLoading = ref(false)

  async function fetchBoards() {
    loading.value = true
    try {
      const { data } = await boardsApi.list()
      boards.value = data
    } finally {
      loading.value = false
    }
  }

  async function createBoard(title: string, description?: string) {
    const { data } = await boardsApi.create(title, description)
    boards.value.unshift(data)
    return data
  }

  async function deleteBoard(boardId: string) {
    await boardsApi.delete(boardId)
    boards.value = boards.value.filter(b => b.id !== boardId)
    if (currentBoard.value?.id === boardId) currentBoard.value = null
  }

  async function fetchBoard(id: string) {
    boardLoading.value = true
    try {
      const { data } = await boardsApi.get(id)
      currentBoard.value = data
    } finally {
      boardLoading.value = false
    }
  }

  async function updateBoard(boardId: string, title: string, description?: string | null) {
    const { data } = await boardsApi.update(boardId, { title, description: description ?? undefined })
    if (currentBoard.value) {
      currentBoard.value.title = data.title
      currentBoard.value.description = data.description
    }
    const idx = boards.value.findIndex(b => b.id === boardId)
    if (idx !== -1) {
      boards.value[idx].title = data.title
      boards.value[idx].description = data.description
    }
    return data
  }

  async function createColumn(boardId: string, title: string) {
    const { data } = await columnsApi.create(boardId, title)
    currentBoard.value?.columns.push(data)
    return data
  }

  async function deleteColumn(columnId: string) {
    await columnsApi.delete(columnId)
    if (currentBoard.value) {
      currentBoard.value.columns = currentBoard.value.columns.filter(c => c.id !== columnId)
    }
  }

  async function updateColumn(columnId: string, title: string) {
    const { data } = await columnsApi.update(columnId, { title })
    if (currentBoard.value) {
      const col = currentBoard.value.columns.find(c => c.id === columnId)
      if (col) col.title = data.title
    }
  }

  async function createCard(columnId: string, title: string) {
    const { data } = await cardsApi.create(columnId, title)
    const col = currentBoard.value?.columns.find(c => c.id === columnId)
    col?.cards.push(data)
    return data
  }

  async function deleteCard(cardId: string) {
    await cardsApi.delete(cardId)
    if (currentBoard.value) {
      for (const col of currentBoard.value.columns) {
        const idx = col.cards.findIndex(c => c.id === cardId)
        if (idx !== -1) { col.cards.splice(idx, 1); break }
      }
    }
    if (activeCard.value?.id === cardId) activeCard.value = null
  }

  async function moveCard(cardId: string, fromColumnId: string, toColumnId: string, position: number) {
    if (!currentBoard.value) return

    // Оптимистичное обновление
    const fromCol = currentBoard.value.columns.find(c => c.id === fromColumnId)
    const toCol = currentBoard.value.columns.find(c => c.id === toColumnId)
    if (!fromCol || !toCol) return

    const cardIndex = fromCol.cards.findIndex(c => c.id === cardId)
    if (cardIndex === -1) return
    const [card] = fromCol.cards.splice(cardIndex, 1)
    card.column_id = toColumnId
    card.position = position
    toCol.cards.push(card)
    toCol.cards.sort((a, b) => a.position - b.position)

    try {
      await cardsApi.move(cardId, toColumnId, position)
    } catch {
      // Откат при ошибке
      await fetchBoard(currentBoard.value.id)
    }
  }

  async function openCard(cardId: string) {
    const { data } = await cardsApi.get(cardId)
    activeCard.value = data
  }

  function closeCard() {
    activeCard.value = null
  }

  async function createBoardLabel(boardId: string, name: string, color: string) {
    const { data } = await boardsApi.createLabel(boardId, name, color)
    currentBoard.value?.labels.push(data)
    return data
  }

  async function updateBoardLabel(labelId: string, name: string, color: string) {
    const { data } = await boardsApi.updateLabel(labelId, name, color)
    if (currentBoard.value) {
      const idx = currentBoard.value.labels.findIndex(l => l.id === labelId)
      if (idx !== -1) currentBoard.value.labels[idx] = data
      // Sync label in all cards
      for (const col of currentBoard.value.columns) {
        for (const card of col.cards) {
          const ci = card.labels.findIndex(l => l.id === labelId)
          if (ci !== -1) card.labels[ci] = data
        }
      }
    }
    return data
  }

  async function deleteBoardLabel(labelId: string) {
    await boardsApi.deleteLabel(labelId)
    if (currentBoard.value) {
      currentBoard.value.labels = currentBoard.value.labels.filter(l => l.id !== labelId)
      for (const col of currentBoard.value.columns) {
        for (const card of col.cards) {
          card.labels = card.labels.filter(l => l.id !== labelId)
        }
      }
    }
  }

  async function updateColumnPositions(_boardId?: string) {
    if (!currentBoard.value) return
    const updates = currentBoard.value.columns.map((col, i) =>
      columnsApi.update(col.id, { position: (i + 1) * 1000 })
    )
    await Promise.all(updates)
  }

  return {
    boards,
    currentBoard,
    activeCard,
    loading,
    boardLoading,
    fetchBoards,
    createBoard,
    deleteBoard,
    fetchBoard,
    updateBoard,
    createColumn,
    deleteColumn,
    updateColumn,
    createCard,
    deleteCard,
    moveCard,
    openCard,
    closeCard,
    updateColumnPositions,
    createBoardLabel,
    updateBoardLabel,
    deleteBoardLabel,
  }
})
