<template>
  <div class="layout">
    <el-container style="height: 100vh;">
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <el-icon size="32" color="#409EFF"><FirstAidKit /></el-icon>
          <span>医保智能审核</span>
        </div>
        <el-menu
          :default-active="$route.path"
          class="el-menu-vertical"
          :router="true"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.title }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-tag type="success" effect="light">系统运行正常</el-tag>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const menuItems = [
  { path: '/chat', title: '智能对话', icon: 'ChatDotRound' },
  { path: '/patients', title: '患者管理', icon: 'User' }
]

const currentTitle = computed(() => {
  const current = menuItems.find(item => item.path === route.path)
  return current?.title || '首页'
})
</script>

<style scoped>
.layout {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  background-color: #2b3649;
  border-bottom: 1px solid #1f2d3d;
}

.logo span {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin-left: 12px;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
