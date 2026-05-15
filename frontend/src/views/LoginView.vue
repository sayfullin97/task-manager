<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

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
  <div class="min-h-screen flex items-center justify-center bg-muted/30">
    <Card class="w-full max-w-md p-8 space-y-6">
      <div class="space-y-2 text-center">
        <h1 class="text-2xl font-bold">Welcome back</h1>
        <p class="text-muted-foreground text-sm">Sign in to your account</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <div class="space-y-1">
          <label class="text-sm font-medium">Email</label>
          <Input v-model="email" type="email" placeholder="you@example.com" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">Password</label>
          <Input v-model="password" type="password" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-destructive text-sm">{{ error }}</p>

        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </Button>
      </form>

      <p class="text-center text-sm text-muted-foreground">
        No account?
        <RouterLink to="/register" class="text-primary hover:underline font-medium">Sign up</RouterLink>
      </p>
    </Card>
  </div>
</template>
