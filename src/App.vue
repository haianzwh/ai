<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatArea from './components/ChatArea.vue'
import TopBar from './components/TopBar.vue'
import SettingsModal from './components/SettingsModal.vue'
import { getSessions, createSession, getModels, sendMessage, setModel, compactSession, interruptSession } from './api/opencode'
import type { Session, Message, Model } from './api/opencode'

const sessions = ref<Session[]>([])
const currentSession = ref<Session | null>(null)
const messages = ref<Message[]>([])
const models = ref<Model[]>([])
const currentModel = ref('')
const isLoading = ref(false)
const showSettings = ref(false)
const sidebarCollapsed = ref(false)

onMounted(async () => {
  await loadSessions()
  await loadModels()
})

async function loadSessions() {
  try {
    sessions.value = await getSessions()
  } catch (e) {
    console.error('Failed to load sessions:', e)
  }
}

async function loadModels() {
  try {
    models.value = await getModels()
    if (models.value.length > 0) {
      currentModel.value = models.value[0].id
    }
  } catch (e) {
    console.error('Failed to load models:', e)
  }
}

async function selectSession(session: Session) {
  currentSession.value = session
  messages.value = []
  currentModel.value = session.model?.id || currentModel.value
}

async function newSession() {
  try {
    const session = await createSession()
    sessions.value.unshift(session)
    currentSession.value = session
    messages.value = []
  } catch (e) {
    console.error('Failed to create session:', e)
  }
}

async function handleSend(content: string) {
  if (!currentSession.value || isLoading.value) return

  const userMsg: Message = {
    id: `user-${Date.now()}`,
    role: 'user',
    content,
    timestamp: new Date()
  }
  messages.value.push(userMsg)

  const assistantMsg: Message = {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: '',
    thinking: '',
    timestamp: new Date(),
    isStreaming: true
  }
  messages.value.push(assistantMsg)
  isLoading.value = true

  try {
    await sendMessage(
      currentSession.value.id,
      content,
      (text, thinking) => {
        if (text) assistantMsg.content += text
        if (thinking) assistantMsg.thinking = (assistantMsg.thinking || '') + thinking
      },
      () => {
        assistantMsg.isStreaming = false
        isLoading.value = false
        loadSessions()
      }
    )
  } catch (e) {
    console.error('Failed to send message:', e)
    assistantMsg.content = '抱歉，发送消息失败，请重试。'
    assistantMsg.isStreaming = false
    isLoading.value = false
  }
}

async function handleModelChange(modelId: string) {
  if (currentSession.value) {
    await setModel(currentSession.value.id, modelId)
    currentModel.value = modelId
  }
}

async function handleCompact() {
  if (currentSession.value) {
    await compactSession(currentSession.value.id)
  }
}

async function handleInterrupt() {
  if (currentSession.value && isLoading.value) {
    await interruptSession(currentSession.value.id)
    isLoading.value = false
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg?.isStreaming) {
      lastMsg.isStreaming = false
    }
  }
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div class="app-container">
    <Sidebar
      :sessions="sessions"
      :current-session="currentSession"
      :collapsed="sidebarCollapsed"
      @select="selectSession"
      @new-session="newSession"
      @toggle="toggleSidebar"
    />

    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <TopBar
        :models="models"
        :current-model="currentModel"
        :is-loading="isLoading"
        @model-change="handleModelChange"
        @settings="showSettings = true"
        @compact="handleCompact"
        @interrupt="handleInterrupt"
      />

      <ChatArea
        :messages="messages"
        :is-loading="isLoading"
        :has-session="!!currentSession"
        @send="handleSend"
        @new-session="newSession"
      />
    </main>

    <SettingsModal
      v-if="showSettings"
      @close="showSettings = false"
    />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #f7f7f8;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
}

.sidebar-collapsed {
  margin-left: 0;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
