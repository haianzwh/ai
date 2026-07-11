<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import ChatMessage from './ChatMessage.vue'
import type { Message } from '../api/opencode'

const props = defineProps<{
  messages: Message[]
  isLoading: boolean
  hasSession: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
  'new-session': []
}>()

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

watch(() => props.messages.length, async () => {
  await nextTick()
  scrollToBottom()
})

watch(() => props.messages.map(m => m.content), () => {
  nextTick(() => scrollToBottom())
}, { deep: true })

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handleSend() {
  if (!inputText.value.trim() || props.isLoading) return
  emit('send', inputText.value.trim())
  inputText.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleTextareaInput(e: Event) {
  const textarea = e.target as HTMLTextAreaElement
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
}
</script>

<template>
  <div class="chat-area">
    <div class="messages-container" ref="messagesContainer">
      <div v-if="!hasSession" class="welcome-screen">
        <div class="welcome-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <h2>开始新的对话</h2>
        <p>选择左侧会话或创建新对话</p>
        <button class="start-btn" @click="$emit('new-session')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          新建会话
        </button>
      </div>

      <div v-else-if="!messages.length" class="empty-chat">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <h3>开始对话</h3>
        <p>输入你的问题，AI 将为你解答</p>
      </div>

      <template v-else>
        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />
      </template>
    </div>

    <div class="input-area">
      <div class="input-wrapper">
        <textarea
          v-model="inputText"
          @keydown="handleKeydown"
          @input="handleTextareaInput"
          placeholder="输入你的问题..."
          :disabled="isLoading || !hasSession"
          rows="1"
        ></textarea>
        <button
          class="send-btn"
          @click="handleSend"
          :disabled="!inputText.trim() || isLoading || !hasSession"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>
      <div class="input-hint">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  color: #4a9eff;
  margin-bottom: 24px;
}

.welcome-icon svg {
  width: 100%;
  height: 100%;
}

.welcome-screen h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.welcome-screen p {
  font-size: 14px;
  color: #999;
  margin: 0 0 24px;
}

.start-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #4a9eff;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.start-btn:hover {
  background: #3a8eef;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
}

.start-btn svg {
  width: 18px;
  height: 18px;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #ccc;
  margin-bottom: 16px;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-chat h3 {
  font-size: 18px;
  font-weight: 500;
  color: #666;
  margin: 0 0 8px;
}

.empty-chat p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.input-area {
  padding: 16px 24px 24px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
  background: #f7f7f8;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: #4a9eff;
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #333;
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  outline: none;
  font-family: inherit;
  min-height: 24px;
  max-height: 200px;
}

textarea::placeholder {
  color: #999;
}

textarea:disabled {
  opacity: 0.5;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: #4a9eff;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #3a8eef;
  transform: scale(1.05);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}

.input-hint {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .messages-container {
    padding: 16px;
  }

  .input-area {
    padding: 12px 16px 16px;
  }
}
</style>
