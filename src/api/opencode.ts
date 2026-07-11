const API_BASE = ''

export interface Session {
  id: string
  title: string
  time: { created: number; updated: number }
  model: { id: string; providerID: string }
  tokens: { input: number; output: number; reasoning: number }
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  timestamp: Date
  isStreaming?: boolean
}

export interface Model {
  id: string
  name: string
  providerID: string
}

export interface Provider {
  id: string
  name: string
}

export async function getSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/api/session`)
  const data = await res.json()
  return data.data || []
}

export async function createSession(): Promise<Session> {
  const res = await fetch(`${API_BASE}/api/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
  const data = await res.json()
  return data.data
}

export async function getSession(id: string): Promise<Session> {
  const res = await fetch(`${API_BASE}/api/session/${id}`)
  const data = await res.json()
  return data.data
}

export async function deleteSession(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/session/${id}`, { method: 'DELETE' })
}

export async function getModels(): Promise<Model[]> {
  const res = await fetch(`${API_BASE}/api/model`)
  const data = await res.json()
  const models = data.data || []
  return models.filter((m: any) => m.status === 'active')
}

export async function getProviders(): Promise<Provider[]> {
  const res = await fetch(`${API_BASE}/api/provider`)
  const data = await res.json()
  return data.data || []
}

export async function sendMessage(
  sessionId: string,
  content: string,
  onChunk: (text: string, thinking?: string) => void,
  onDone: () => void
): Promise<void> {
  // 先获取当前消息数量
  const initialRes = await fetch(`${API_BASE}/api/session/${sessionId}/message`)
  const initialData = await initialRes.json()
  const initialMessages = initialData.data || []
  const initialCount = initialMessages.length
  
  // 发送 prompt
  const res = await fetch(`${API_BASE}/api/session/${sessionId}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: { text: content } })
  })

  if (!res.ok) {
    throw new Error(`Failed to send message: ${res.status}`)
  }

  let foundNewAssistant = false
  
  const pollInterval = setInterval(async () => {
    try {
      const msgRes = await fetch(`${API_BASE}/api/session/${sessionId}/message`)
      const msgData = await msgRes.json()
      const messages = msgData.data || []
      
      // 检查是否有新消息
      if (messages.length > initialCount) {
        const latestMsg = messages[0]
        
        // 检查是否是新的 assistant 消息且已完成
        if (latestMsg.type === 'assistant' && latestMsg.finish === 'stop') {
          const textContent = latestMsg.content?.find((c: any) => c.type === 'text')
          if (textContent?.text && !foundNewAssistant) {
            foundNewAssistant = true
            onChunk(textContent.text)
            clearInterval(pollInterval)
            onDone()
            return
          }
        }
      }
    } catch (e) {
      console.error('Poll error:', e)
    }
  }, 500)
  
  setTimeout(() => {
    clearInterval(pollInterval)
    onDone()
  }, 30000)
}

export async function setModel(sessionId: string, modelId: string): Promise<void> {
  await fetch(`${API_BASE}/api/session/${sessionId}/model`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: modelId })
  })
}

export async function compactSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/api/session/${sessionId}/compact`, {
    method: 'POST'
  })
}

export async function interruptSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/api/session/${sessionId}/interrupt`, {
    method: 'POST'
  })
}
