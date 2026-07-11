<script setup lang="ts">
import { computed } from 'vue'
import type { Session } from '../api/opencode'

const props = defineProps<{
  sessions: Session[]
  currentSession: Session | null
  collapsed: boolean
}>()

const emit = defineEmits<{
  select: [session: Session]
  'new-session': []
  toggle: []
}>()

const today = computed(() => {
  const now = Date.now()
  const day = 24 * 60 * 60 * 1000
  return props.sessions.filter(s => now - s.time.updated < day)
})

const yesterday = computed(() => {
  const now = Date.now()
  const day = 24 * 60 * 60 * 1000
  return props.sessions.filter(s => {
    const age = now - s.time.updated
    return age >= day && age < 2 * day
  })
})

const older = computed(() => {
  const now = Date.now()
  const day = 24 * 60 * 60 * 1000
  return props.sessions.filter(s => now - s.time.updated >= 2 * day)
})

function formatTime(timestamp: number): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        <span v-if="!collapsed" class="logo-text">AI Chat</span>
      </div>
      <button class="new-chat-btn" @click="$emit('new-session')" title="新建会话">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14" />
        </svg>
      </button>
    </div>

    <div class="session-list" v-if="!collapsed">
      <div v-if="today.length" class="session-group">
        <div class="group-title">今天</div>
        <div
          v-for="session in today"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSession?.id === session.id }"
          @click="$emit('select', session)"
        >
          <div class="session-title">{{ session.title || '新对话' }}</div>
          <div class="session-time">{{ formatTime(session.time.updated) }}</div>
        </div>
      </div>

      <div v-if="yesterday.length" class="session-group">
        <div class="group-title">昨天</div>
        <div
          v-for="session in yesterday"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSession?.id === session.id }"
          @click="$emit('select', session)"
        >
          <div class="session-title">{{ session.title || '新对话' }}</div>
          <div class="session-time">{{ formatTime(session.time.updated) }}</div>
        </div>
      </div>

      <div v-if="older.length" class="session-group">
        <div class="group-title">更早</div>
        <div
          v-for="session in older"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSession?.id === session.id }"
          @click="$emit('select', session)"
        >
          <div class="session-title">{{ session.title || '新对话' }}</div>
          <div class="session-time">{{ formatTime(session.time.updated) }}</div>
        </div>
      </div>

      <div v-if="!sessions.length" class="empty-sessions">
        <p>暂无会话</p>
        <p class="hint">点击上方按钮开始新对话</p>
      </div>
    </div>

    <div class="sidebar-footer">
      <button class="toggle-btn" @click="$emit('toggle')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path v-if="collapsed" d="M9 18l6-6-6-6" />
          <path v-else d="M15 18l-6-6 6-6" />
        </svg>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1a1a1a;
}

.logo svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.new-chat-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: #f0f0f0;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.new-chat-btn svg {
  width: 18px;
  height: 18px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 8px;
}

.session-group {
  margin-bottom: 16px;
}

.group-title {
  font-size: 12px;
  color: #999;
  padding: 8px 12px 4px;
  font-weight: 500;
}

.session-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 2px;
}

.session-item:hover {
  background: #f5f5f5;
}

.session-item.active {
  background: #e8f4ff;
}

.session-title {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.empty-sessions {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-sessions p {
  margin: 0;
}

.empty-sessions .hint {
  font-size: 12px;
  margin-top: 8px;
  color: #bbb;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #f0f0f0;
}

.toggle-btn svg {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 280px;
  }
}
</style>
