<script setup lang="ts">
import { computed, ref } from 'vue'
import { marked } from 'marked'
import type { Message } from '../api/opencode'

marked.use({
  breaks: true,
  gfm: true
})

const props = defineProps<{
  message: Message
}>()

const showThinking = ref(false)

const isUser = computed(() => props.message.role === 'user')

const hasThinking = computed(() => !!props.message.thinking)

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked.parse(props.message.content) as string
})

const formattedTime = computed(() => {
  return props.message.timestamp.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<template>
  <div class="message-wrapper" :class="{ 'user-message': isUser, 'assistant-message': !isUser }">
    <div class="message-avatar">
      <div v-if="isUser" class="avatar user-avatar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      </div>
      <div v-else class="avatar ai-avatar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      </div>
    </div>

    <div class="message-body">
      <div class="message-header">
        <span class="message-role">{{ isUser ? '你' : 'AI 助手' }}</span>
        <span class="message-time">{{ formattedTime }}</span>
      </div>

      <div v-if="hasThinking" class="thinking-section">
        <button class="thinking-toggle" @click="showThinking = !showThinking">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="thinking-icon" :class="{ expanded: showThinking }">
            <path d="M9 18l6-6-6-6" />
          </svg>
          <span>思考过程</span>
        </button>
        <div v-show="showThinking" class="thinking-content">
          <div class="thinking-text">{{ message.thinking }}</div>
        </div>
      </div>

      <div class="message-content" :class="{ 'streaming': message.isStreaming }">
        <div v-if="isUser" class="user-text">{{ message.content }}</div>
        <div v-else class="markdown-content" v-html="renderedContent"></div>
        <span v-if="message.isStreaming && !message.content" class="typing-indicator">
          <span></span><span></span><span></span>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar svg {
  width: 20px;
  height: 20px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.ai-avatar {
  background: linear-gradient(135deg, #4a9eff 0%, #0066cc 100%);
  color: #fff;
}

.message-body {
  flex: 1;
  min-width: 0;
}

.user-message .message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.message-role {
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.thinking-section {
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
}

.thinking-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: none;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.thinking-toggle:hover {
  background: #f0f0f0;
}

.thinking-icon {
  width: 14px;
  height: 14px;
  transition: transform 0.2s;
}

.thinking-icon.expanded {
  transform: rotate(90deg);
}

.thinking-content {
  padding: 0 12px 10px;
  border-top: 1px solid #e8e8e8;
}

.thinking-text {
  font-size: 13px;
  color: #888;
  line-height: 1.6;
  white-space: pre-wrap;
  font-style: italic;
  padding-top: 8px;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 100%;
}

.user-message .message-content {
  background: linear-gradient(135deg, #4a9eff 0%, #0066cc 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.assistant-message .message-content {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-bottom-left-radius: 4px;
}

.user-text {
  font-size: 15px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.markdown-content {
  font-size: 15px;
  line-height: 1.7;
  color: #333;
}

.markdown-content :deep(p) {
  margin: 0 0 12px;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  margin: 16px 0 12px;
  font-weight: 600;
  color: #1a1a1a;
}

.markdown-content :deep(h1) { font-size: 20px; }
.markdown-content :deep(h2) { font-size: 18px; }
.markdown-content :deep(h3) { font-size: 16px; }

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

.markdown-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  color: #e83e8c;
}

.markdown-content :deep(pre) {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.5;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #4a9eff;
  padding-left: 12px;
  margin: 12px 0;
  color: #666;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e8e8e8;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background: #f5f5f5;
  font-weight: 600;
}

.markdown-content :deep(a) {
  color: #4a9eff;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.streaming {
  position: relative;
}

.streaming::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  width: 2px;
  height: 18px;
  background: #4a9eff;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@media (max-width: 768px) {
  .message-wrapper {
    gap: 8px;
    margin-bottom: 16px;
  }

  .avatar {
    width: 32px;
    height: 32px;
  }

  .avatar svg {
    width: 18px;
    height: 18px;
  }

  .message-content {
    padding: 10px 14px;
  }

  .markdown-content {
    font-size: 14px;
  }
}
</style>
