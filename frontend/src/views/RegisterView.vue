<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

const router = useRouter()
const auth = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!name.value || !email.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    await auth.register(email.value, password.value, name.value)
    router.push('/boards')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <Card class="w-full max-w-sm px-6 py-6 gap-6">
      <div class="text-center">
        <h1 class="text-xl font-semibold">Create account</h1>
        <p class="text-muted-foreground text-sm mt-1">Start managing your tasks today</p>
      </div>

      <form class="flex flex-col gap-3" @submit.prevent="submit">
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium">Name</label>
          <Input v-model="name" placeholder="Your name" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium">Email</label>
          <Input v-model="email" type="email" placeholder="you@example.com" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium">Password</label>
          <Input v-model="password" type="password" placeholder="••••••••" />
        </div>
        <p v-if="error" class="text-destructive text-xs">{{ error }}</p>
        <Button type="submit" class="w-full mt-1" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </Button>
      </form>

      <p class="text-center text-xs text-muted-foreground">
        Already have an account?
        <RouterLink to="/login" class="text-primary hover:underline font-medium">Sign in</RouterLink>
      </p>
    </Card>
  </div>
</template>
