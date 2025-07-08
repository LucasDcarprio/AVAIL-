import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// 页面组件
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import Layout from '../components/Layout.vue'
import Profile from '../views/Profile.vue'
import Attendance from '../views/Attendance.vue'
import AttendanceHistory from '../views/AttendanceHistory.vue'
import LeaveRequest from '../views/LeaveRequest.vue'
import ExpenseReport from '../views/ExpenseReport.vue'
import WorkDiary from '../views/WorkDiary.vue'
import OutingReport from '../views/OutingReport.vue'
import Schedule from '../views/Schedule.vue'
import AdminUsers from '../views/admin/Users.vue'
import AdminSettings from '../views/admin/Settings.vue'
import AdminAttendance from '../views/admin/Attendance.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: Attendance
      },
      {
        path: 'attendance/history',
        name: 'AttendanceHistory',
        component: AttendanceHistory
      },
      {
        path: 'leave',
        name: 'LeaveRequest',
        component: LeaveRequest
      },
      {
        path: 'expense',
        name: 'ExpenseReport',
        component: ExpenseReport
      },
      {
        path: 'diary',
        name: 'WorkDiary',
        component: WorkDiary
      },
      {
        path: 'outing',
        name: 'OutingReport',
        component: OutingReport
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: Schedule
      },
      {
        path: 'admin/users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/settings',
        name: 'AdminSettings',
        component: AdminSettings,
        meta: { requiresAdmin: true }
      },
      {
        path: 'admin/attendance',
        name: 'AdminAttendance',
        component: AdminAttendance,
        meta: { requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  const userRole = store.getters.userRole

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/')
  } else if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router