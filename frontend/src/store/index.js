import { createStore } from 'vuex'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

// 配置axios
axios.defaults.baseURL = API_BASE_URL
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
    },
    
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    SET_ERROR(state, error) {
      state.error = error
    },
    
    CLEAR_ERROR(state) {
      state.error = null
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        const response = await axios.post('/auth/login', credentials)
        const { access_token, user } = response.data
        
        commit('SET_TOKEN', access_token)
        commit('SET_USER', user)
        
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.error || '登录失败'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        commit('CLEAR_ERROR')
        
        const response = await axios.post('/auth/register', userData)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.error || '注册失败'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
      commit('CLEAR_ERROR')
    },
    
    async fetchProfile({ commit }) {
      try {
        const response = await axios.get('/auth/profile')
        commit('SET_USER', response.data.user)
        return response.data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },
    
    async updateProfile({ commit }, profileData) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.put('/auth/profile', profileData)
        // 更新本地用户信息
        await this.dispatch('fetchProfile')
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.error || '更新失败'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async changePassword({ commit }, passwordData) {
      try {
        commit('SET_LOADING', true)
        const response = await axios.post('/auth/change-password', passwordData)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.error || '修改密码失败'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    userRole: state => state.user?.role || 'employee',
    isAdmin: state => state.user?.role === 'admin',
    isLoading: state => state.loading,
    error: state => state.error
  }
})

export { axios }