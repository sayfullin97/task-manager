<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!email.value || !password.value) return
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/boards')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <Card class="w-full max-w-sm px-6 py-6 gap-6">
      <div class="text-center">
        <h1 class="text-xl font-semibold">Welcome back</h1>
        <p class="text-muted-foreground text-sm mt-1">Sign in to your account</p>
      </div>

      <form class="flex flex-col gap-3" @submit.prevent="submit">
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
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </Button>
      </form>

      <p class="text-center text-xs text-muted-foreground">
        No account?
        <RouterLink to="/register" class="text-primary hover:underline font-medium">Sign up</RouterLink>
      </p>
    </Card>
  </div>
</template>
