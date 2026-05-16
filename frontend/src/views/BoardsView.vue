<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBoardsStore } from '@/stores/boards'
import { useToastStore } from '@/stores/toast'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useBoardsStore()
const toast = useToastStore()

const showCreate = ref(false)
const newTitle = ref('')
const creating = ref(false)

onMounted(() => store.fetchBoards())

async function createBoard() {
  if (!newTitle.value.trim()) return
  creating.value = true
  try {
    const board = await store.createBoard(newTitle.value.trim())
    newTitle.value = ''
    showCreate.value = false
    toast.success('Доска создана')
    router.push(`/boards/${board.id}`)
  } finally {
    creating.value = false
  }
}

function logout() {
  auth.logout()
  router.push('/login')
}

const COLORS = ['bg-blue-500', 'bg-violet-500', 'bg-rose-500', 'bg-emerald-500', 'bg-amber-500', 'bg-cyan-500']
function boardColor(id: string) {
  const idx = id.charCodeAt(0) % COLORS.length
  return COLORS[idx]
}
</script>

<template>
  <div class="min-h-screen bg-muted/20">
    <!-- Header -->
    <header class="border-b bg-background px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold">Task Manager</h1>
      <div class="flex items-center gap-3">
        <span class="text-sm text-muted-foreground">{{ auth.user?.name }}</span>
        <Button variant="outline" size="sm" @click="logout">Logout</Button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-semibold">My Boards</h2>
        <Button @click="showCreate = true">+ New Board</Button>
      </div>

      <!-- Create board form -->
      <Card v-if="showCreate" class="p-4 mb-6 max-w-sm">
        <div class="space-y-3">
          <Input v-model="newTitle" placeholder="Board title" autofocus @keyup.enter="createBoard" />
          <div class="flex gap-2">
            <Button size="sm" :disabled="creating" @click="createBoard">
              {{ creating ? 'Creating...' : 'Create' }}
            </Button>
            <Button size="sm" variant="ghost" @click="showCreate = false; newTitle = ''">Cancel</Button>
          </div>
        </div>
      </Card>

      <!-- Boards grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <RouterLink
          v-for="board in store.boards"
          :key="board.id"
          :to="`/boards/${board.id}`"
          class="group"
        >
          <div class="rounded-lg overflow-hidden border hover:shadow-md transition-shadow cursor-pointer">
            <div :class="[boardColor(board.id), 'h-20']" />
            <div class="p-3 bg-card">
              <p class="font-medium text-sm truncate">{{ board.title }}</p>
              <p v-if="board.description" class="text-xs text-muted-foreground mt-0.5 truncate">{{ board.description }}</p>
              <p class="text-xs text-muted-foreground mt-1 capitalize">{{ board.role }}</p>
            </div>
          </div>
        </RouterLink>

        <p v-if="!store.boards.length" class="col-span-full text-center text-muted-foreground py-12">
          No boards yet. Create your first one!
        </p>
      </div>
    </main>
  </div>
</template>
