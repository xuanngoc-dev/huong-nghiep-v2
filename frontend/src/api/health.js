import api from '@/api/axios'

export function getHealth() {
  return api.get('/health').then((res) => res.data)
}

export function getDatabaseHealth() {
  return api.get('/health/db').then((res) => res.data)
}
