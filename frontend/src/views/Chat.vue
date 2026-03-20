<template>
  <div class="chat-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- 左侧：会话历史 -->
      <el-col :span="5" style="height: 100%;">
        <el-card class="session-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>会话历史</span>
              <el-button type="primary" size="small" @click="startNewChat">
                <el-icon><Plus /></el-icon> 新对话
              </el-button>
            </div>
          </template>

          <div class="session-list">
            <div
              v-for="session in sessions"
              :key="session.session_id"
              class="session-item"
              :class="{ active: currentSessionId === session.session_id }"
              @click="loadSession(session.session_id)"
            >
              <div class="session-title">会话 {{ session.session_id.slice(0, 8) }}</div>
              <div class="session-time">{{ formatDate(session.last_message_time) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：对话区域 -->
      <el-col :span="19" style="height: 100%;">
        <el-card class="chat-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>智能对话</span>
              <el-tag type="info" size="small">DeepSeek</el-tag>
            </div>
          </template>

          <!-- 消息列表 -->
          <div ref="messageContainer" class="message-container">
            <div v-for="(msg, index) in messages" :key="index" class="message-wrapper"
                 :class="{ 'user-message': msg.role === 'user', 'assistant-message': msg.role === 'assistant' }">
              <div class="message-avatar">
                <el-avatar :size="36" :icon="msg.role === 'user' ? 'UserFilled' : 'FirstAidKit'"
                          :style="{ background: msg.role === 'user' ? '#409EFF' : '#67C23A' }" />
              </div>
              <div class="message-content">
                <div v-if="msg.role === 'assistant'" class="message-text" v-html="renderMarkdown(msg.content)"></div>
                <div v-else class="message-text">{{ msg.content }}</div>
                <div class="message-time">{{ formatTime(msg.time) }}</div>
              </div>
            </div>

            <!-- 加载指示器 -->
            <div v-if="loading" class="message-wrapper assistant-message">
              <div class="message-avatar">
                <el-avatar :size="36" icon="FirstAidKit" style="background: #67C23A;" />
              </div>
              <div class="message-content">
                <el-skeleton :rows="2" animated />
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="请输入您的问题，例如：
- 如何使用本系统？
- 医保审核的规则有哪些？
- 解释违规类型"
              @keydown.enter.prevent="sendMessage"
            />
            <div class="input-actions">
              <span class="hint">按 Enter 发送，Shift + Enter 换行</span>
              <el-button
                type="primary"
                :loading="loading"
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              >
                发送 <el-icon class="el-icon--right"><Position /></el-icon>
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { streamChat, getChatHistory, getChatSessions } from '@/api'

// 状态
const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是医保智能审核助手。\n\n我可以帮您：\n1. **了解系统功能** - 解答使用问题\n2. **查询审核规则** - 解释各类违规规则\n3. **医保政策咨询** - 回答相关政策问题\n\n请问有什么可以帮助您的？',
    time: new Date()
  }
])
const inputMessage = ref('')
const loading = ref(false)
const messageContainer = ref(null)

// 渲染Markdown
const renderMarkdown = (text) => {
  return marked(text || '')
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 格式化日期
const formatDate = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getMonth() + 1}/${date.getDate()} ${formatTime(time)}`
}

// 获取会话列表
const loadSessions = async () => {
  try {
    const res = await getChatSessions()
    sessions.value = res.sessions || []
  } catch (error) {
    console.error('获取会话列表失败:', error)
  }
}

// 加载会话历史
const loadSession = async (sessionId) => {
  try {
    const res = await getChatHistory(sessionId)
    currentSessionId.value = sessionId

    if (res.messages && res.messages.length > 0) {
      messages.value = res.messages.map(m => ({
        role: m.role,
        content: m.content,
        time: new Date(m.created_at)
      })).reverse()
    }
  } catch (error) {
    ElMessage.error('加载会话失败')
  }
}

// 开始新对话
const startNewChat = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '已开启新对话。请问有什么可以帮助您的？',
      time: new Date()
    }
  ]
  currentSessionId.value = null
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  messages.value.push({
    role: 'user',
    content: userMessage,
    time: new Date()
  })

  inputMessage.value = ''
  loading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    let assistantContent = ''

    // 流式接收响应
    await streamChat({
      message: userMessage,
      session_id: currentSessionId.value,
      onMessage: (chunk) => {
        assistantContent += chunk
        // 更新最后一条消息
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg.role === 'assistant') {
          lastMsg.content = assistantContent
        } else {
          messages.value.push({
            role: 'assistant',
            content: assistantContent,
            time: new Date()
          })
        }
        scrollToBottom()
      },
      onSessionId: (id) => {
        currentSessionId.value = id
      }
    })

    // 刷新会话列表
    await loadSessions()

  } catch (error) {
    ElMessage.error('发送消息失败: ' + error.message)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，系统出现错误，请稍后再试。',
      time: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 监听消息变化自动滚动
watch(() => messages.value.length, () => {
  nextTick(() => scrollToBottom())
})

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 100px);
}

.session-card, .chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.session-card :deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-list {
  max-height: 100%;
  overflow-y: auto;
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
  border: 1px solid #e4e7ed;
}

.session-item:hover {
  background-color: #f5f7fa;
}

.session-item.active {
  background-color: #ecf5ff;
  border-color: #409eff;
}

.session-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.session-time {
  font-size: 12px;
  color: #909399;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8f9fa;
}

.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-message .message-content {
  background-color: #409eff;
  color: #fff;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-text :deep(p) {
  margin: 0 0 8px;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-text :deep(ul), .message-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

.message-text :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
  text-align: right;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.input-area {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  background-color: #fff;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.hint {
  font-size: 12px;
  color: #909399;
}
</style>
