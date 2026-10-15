import { computed, reactive, watch } from 'vue'
import { defineStore } from 'pinia'
import { hoiChatStream, layDanhSachModel } from '@/api/chat'
import { createChatSession, newConversation } from '@/utils/chatSession'
import { useAuthStore } from '@/stores/auth'

export const useChatStore = defineStore('chat', () => {
  const auth = useAuthStore()
  const state = reactive({ messages: newConversation(), draft: '', sending: false, models: [], modelId: '',
    suggestions: [], error: '', loadingModels: false, storageWarning: '', context: null })
  const key = () => `huong-nghiep-chat-v2:${auth.user?.id || 'guest'}`
  const session = createChatSession(state, { stream: hoiChatStream, storage: localStorage, storageKey: key })
  session.restore()
  const model = computed(() => state.models.find(m => m.id === state.modelId))
  let loading = null
  async function loadModels() {
    if (loading) return loading
    state.loadingModels = true
    loading = (async () => {
      try {
        state.models = await layDanhSachModel()
        if (!state.models.some(m => m.id === state.modelId)) {
          state.modelId = (state.models.find(m => m.san_sang) || state.models[0])?.id || ''
        }
        state.error = ''
        session.persist()
      } catch {
        state.error = 'Không tải được danh sách model. Vui lòng thử tải lại.'
      } finally {
        state.loadingModels = false
        loading = null
      }
    })()
    return loading
  }
  watch(() => auth.user?.id, () => { session.restore(); loadModels() })
  watch(() => [state.draft, state.modelId], () => session.persist())
  return { state, model, loadModels, send: session.send, stop: session.stop, clear: session.clear, retry: session.retry }
})
