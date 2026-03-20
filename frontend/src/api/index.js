import axios from 'axios'

const API_BASE = '/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000
})

// ========== 患者管理 ==========
export const getPatients = async () => {
  const res = await api.get('/patients')
  return res.data
}

export const getPatient = async (id) => {
  const res = await api.get(`/patients/${id}`)
  return res.data
}

export const createPatient = async (data) => {
  const res = await api.post('/patients', data)
  return res.data
}

export const searchPatients = async (keyword) => {
  const res = await api.get('/patients/search', { params: { keyword } })
  return res.data
}

export const getPatientCharges = async (patientId) => {
  const res = await api.get(`/patients/${patientId}/charges`)
  return res.data
}

export const createChargeItem = async (patientId, data) => {
  const res = await api.post(`/patients/${patientId}/charges`, data)
  return res.data
}

// ========== 对话聊天 ==========
export const sendMessage = async (data) => {
  const res = await api.post('/chat', data)
  return res.data
}

export const streamChat = async ({ message, session_id, onMessage, onSessionId }) => {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      session_id
    })
  })

  if (!response.ok) {
    throw new Error('请求失败')
  }

  // 获取session_id
  const newSessionId = response.headers.get('X-Session-Id')
  if (newSessionId && onSessionId) {
    onSessionId(newSessionId)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value, { stream: true })
    if (onMessage) {
      onMessage(chunk)
    }
  }
}

export const getChatHistory = async (sessionId) => {
  const res = await api.get(`/chat/history/${sessionId}`)
  return res.data
}

export const getChatSessions = async () => {
  const res = await api.get('/chat/sessions')
  return res.data
}

// ========== 审核管理 ==========
export const auditPatient = async (patientId) => {
  const res = await api.post(`/audit/patient/${patientId}`)
  return res.data
}

export const getAuditResults = async (chargeItemId) => {
  const res = await api.get(`/audit/results/${chargeItemId}`)
  return res.data
}

export const getStatistics = async () => {
  const res = await api.get('/audit/statistics')
  return res.data
}

export const getAuditRules = async () => {
  const res = await api.get('/audit/rules')
  return res.data
}

export default api
