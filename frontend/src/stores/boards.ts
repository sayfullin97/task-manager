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

  async function fetchBoards() {
    const { data } = await boardsApi.list()
    boards.value = data
  }

  async function createBoard(title: string, description?: string) {
    const { data } = await boardsApi.create(title, description)
    boards.value.unshift(data)
    return data
  }

  async function fetchBoard(id: string) {
    const { data } = await boardsApi.get(id)
    currentBoard.value = data
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

  async function createCard(columnId: string, title: string) {
    const { data } = await cardsApi.create(columnId, title)
    const col = currentBoard.value?.columns.find(c => c.id === columnId)
    col?.cards.push(data)
    return data
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
    fetchBoards,
    createBoard,
    fetchBoard,
    createColumn,
    deleteColumn,
    createCard,
    moveCard,
    openCard,
    closeCard,
    updateColumnPositions,
  }
})
