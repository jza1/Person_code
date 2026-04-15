<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="logo">
        <h1>Rayshopping 购物平台</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :router="true"
        class="nav-menu"
      >
        <el-menu-item index="/">商城首页</el-menu-item>
        <el-menu-item index="/cart">购物车</el-menu-item>
        <el-menu-item index="/orders">我的订单</el-menu-item>
        <el-menu-item index="/users">用户管理</el-menu-item>
      </el-menu>
      <div class="current-user">
        <span v-if="currentUser">当前用户: {{ currentUser.nickname || currentUser.username }}</span>
        <el-button v-else type="primary" size="small" @click="showUserSelect">选择用户</el-button>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>

  <el-dialog v-model="userDialogVisible" title="选择用户" width="500px">
    <el-select v-model="selectedUserId" placeholder="请选择用户" style="width: 100%" @change="onUserSelect">
      <el-option
        v-for="user in users"
        :key="user.id"
        :label="user.nickname || user.username"
        :value="user.id"
      />
    </el-select>
    <template #footer>
      <el-button type="primary" @click="createNewUser">创建新用户</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUsers } from '@/api/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const currentUser = ref(null)
const users = ref([])
const userDialogVisible = ref(false)
const selectedUserId = ref(null)

const activeMenu = computed(() => route.path)

onMounted(() => {
  loadUsers()
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
})

async function loadUsers() {
  try {
    const res = await getUsers()
    users.value = res.data
    if (users.value.length === 0) {
      ElMessage.warning('暂无用户，请先创建用户')
    }
  } catch (e) {
    console.error('加载用户失败', e)
    ElMessage.error('无法连接到用户服务，请确认后端服务已启动')
  }
}

function showUserSelect() {
  loadUsers()
  userDialogVisible.value = true
}

function onUserSelect(userId) {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    currentUser.value = user
    localStorage.setItem('currentUser', JSON.stringify(user))
    userDialogVisible.value = false
    ElMessage.success(`已选择用户: ${user.nickname || user.username}`)
  }
}

function createNewUser() {
  userDialogVisible.value = false
  router.push('/users')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}
.app-header {
  display: flex;
  align-items: center;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 0 20px;
}
.logo h1 {
  margin: 0;
  font-size: 20px;
  margin-right: 40px;
}
.nav-menu {
  flex: 1;
  border-bottom: none;
}
.current-user {
  margin-left: 20px;
}
.app-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
