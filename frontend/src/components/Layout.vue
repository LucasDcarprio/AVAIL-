<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
      <div class="sidebar-header">
        <div v-if="!isCollapse" class="logo">
          <el-icon class="logo-icon"><Calendar /></el-icon>
          <span class="logo-text">打卡系统</span>
        </div>
        <el-button
          type="text"
          class="collapse-btn"
          @click="toggleCollapse"
        >
          <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
        </el-button>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>

        <el-menu-item index="/attendance">
          <el-icon><Clock /></el-icon>
          <template #title>考勤打卡</template>
        </el-menu-item>

        <el-menu-item index="/attendance/history">
          <el-icon><Document /></el-icon>
          <template #title>考勤历史</template>
        </el-menu-item>

        <el-sub-menu index="applications">
          <template #title>
            <el-icon><Files /></el-icon>
            <span>申请管理</span>
          </template>
          <el-menu-item index="/leave">
            <el-icon><Calendar /></el-icon>
            <template #title>请假申请</template>
          </el-menu-item>
          <el-menu-item index="/expense">
            <el-icon><Money /></el-icon>
            <template #title>费用报销</template>
          </el-menu-item>
          <el-menu-item index="/outing">
            <el-icon><Position /></el-icon>
            <template #title>外出报备</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/diary">
          <el-icon><EditPen /></el-icon>
          <template #title>工作日报</template>
        </el-menu-item>

        <el-menu-item index="/schedule">
          <el-icon><Grid /></el-icon>
          <template #title>排班查看</template>
        </el-menu-item>

        <!-- 管理员菜单 -->
        <el-sub-menu v-if="isAdmin" index="admin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/settings">
            <el-icon><Tools /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>
          <el-menu-item index="/admin/attendance">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>考勤管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 头部 -->
      <el-header class="header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbList" :key="item.path" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 通知 -->
          <el-badge :value="12" :max="99" class="header-badge">
            <el-button type="text" class="header-btn">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>

          <!-- 用户菜单 -->
          <el-dropdown class="user-dropdown" @command="handleCommand">
            <div class="user-info">
              <el-avatar class="user-avatar">
                {{ currentUser?.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="user-name">{{ currentUser?.real_name || '用户' }}</span>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="password">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="当前密码" prop="current_password">
          <el-input v-model="passwordForm.current_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handlePasswordSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Clock, Document, Files, Calendar, Money, Position,
  EditPen, Grid, Setting, User, Tools, DataAnalysis, Bell,
  ArrowDown, SwitchButton, Lock, Expand, Fold
} from '@element-plus/icons-vue'

export default {
  name: 'Layout',
  components: {
    Monitor, Clock, Document, Files, Calendar, Money, Position,
    EditPen, Grid, Setting, User, Tools, DataAnalysis, Bell,
    ArrowDown, SwitchButton, Lock, Expand, Fold
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    const isCollapse = ref(false)
    const passwordDialogVisible = ref(false)
    const passwordLoading = ref(false)
    const passwordFormRef = ref()

    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })

    const passwordRules = {
      current_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ],
      confirm_password: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    const currentUser = computed(() => store.getters.currentUser)
    const isAdmin = computed(() => store.getters.isAdmin)
    const activeMenu = computed(() => route.path)

    const breadcrumbList = computed(() => {
      const matched = route.matched.filter(item => item.meta && item.meta.title)
      return matched.map(item => ({
        path: item.path,
        title: item.meta.title
      }))
    })

    const toggleCollapse = () => {
      isCollapse.value = !isCollapse.value
    }

    const handleCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/profile')
          break
        case 'password':
          passwordDialogVisible.value = true
          break
        case 'logout':
          handleLogout()
          break
      }
    }

    const handleLogout = () => {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        store.dispatch('logout')
        router.push('/login')
        ElMessage.success('已退出登录')
      }).catch(() => {})
    }

    const handlePasswordSubmit = async () => {
      try {
        await passwordFormRef.value.validate()
        passwordLoading.value = true

        await store.dispatch('changePassword', {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })

        ElMessage.success('密码修改成功')
        passwordDialogVisible.value = false
        
        // 清空表单
        Object.keys(passwordForm).forEach(key => {
          passwordForm[key] = ''
        })
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '修改密码失败')
      } finally {
        passwordLoading.value = false
      }
    }

    // 监听对话框关闭，清空表单
    watch(passwordDialogVisible, (newVal) => {
      if (!newVal) {
        Object.keys(passwordForm).forEach(key => {
          passwordForm[key] = ''
        })
        passwordFormRef.value?.clearValidate()
      }
    })

    return {
      isCollapse,
      passwordDialogVisible,
      passwordLoading,
      passwordFormRef,
      passwordForm,
      passwordRules,
      currentUser,
      isAdmin,
      activeMenu,
      breadcrumbList,
      toggleCollapse,
      handleCommand,
      handlePasswordSubmit
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
}

.sidebar {
  background-color: #304156;
  transition: all 0.3s;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #1f2d3d;
}

.logo {
  display: flex;
  align-items: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 10px;
  font-size: 24px;
  color: #409eff;
}

.collapse-btn {
  color: #bfcbd9;
  border: none;
  background: none;
}

.collapse-btn:hover {
  color: #409eff;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.main-container {
  flex: 1;
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e8eaec;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.breadcrumb {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-badge {
  cursor: pointer;
}

.header-btn {
  font-size: 18px;
  color: #666;
  border: none;
  background: none;
}

.header-btn:hover {
  color: #409eff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background-color: #409eff;
  color: #fff;
  font-weight: bold;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.user-arrow {
  font-size: 12px;
  color: #999;
}

.main-content {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

/* 滚动条样式 */
.sidebar-menu::-webkit-scrollbar {
  width: 6px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: #1f2d3d;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    height: 100vh;
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 15px;
  }
}
</style>