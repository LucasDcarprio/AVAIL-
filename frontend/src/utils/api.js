import { axios } from '../store'

// 考勤相关API
export const attendanceAPI = {
  // 上班打卡
  clockIn() {
    return axios.post('/attendance/clock-in')
  },
  
  // 下班打卡
  clockOut() {
    return axios.post('/attendance/clock-out')
  },
  
  // 获取今天的考勤记录
  getTodayAttendance() {
    return axios.get('/attendance/today')
  },
  
  // 获取考勤历史
  getAttendanceHistory(params) {
    return axios.get('/attendance/history', { params })
  },
  
  // 获取考勤统计
  getAttendanceStatistics(params) {
    return axios.get('/attendance/statistics', { params })
  }
}

// 请假申请API
export const leaveAPI = {
  // 获取请假申请列表
  getLeaveRequests(params) {
    return axios.get('/leave/requests', { params })
  },
  
  // 创建请假申请
  createLeaveRequest(data) {
    return axios.post('/leave/requests', data)
  },
  
  // 获取请假申请详情
  getLeaveRequest(id) {
    return axios.get(`/leave/requests/${id}`)
  },
  
  // 更新请假申请
  updateLeaveRequest(id, data) {
    return axios.put(`/leave/requests/${id}`, data)
  },
  
  // 审批请假申请
  approveLeaveRequest(id, data) {
    return axios.post(`/leave/requests/${id}/approve`, data)
  },
  
  // 删除请假申请
  deleteLeaveRequest(id) {
    return axios.delete(`/leave/requests/${id}`)
  },
  
  // 获取请假类型
  getLeaveTypes() {
    return axios.get('/leave/types')
  }
}

// 费用报销API
export const expenseAPI = {
  // 获取费用报销列表
  getExpenseReports(params) {
    return axios.get('/expense/reports', { params })
  },
  
  // 创建费用报销
  createExpenseReport(data) {
    return axios.post('/expense/reports', data)
  },
  
  // 获取费用报销详情
  getExpenseReport(id) {
    return axios.get(`/expense/reports/${id}`)
  },
  
  // 更新费用报销
  updateExpenseReport(id, data) {
    return axios.put(`/expense/reports/${id}`, data)
  },
  
  // 审批费用报销
  approveExpenseReport(id, data) {
    return axios.post(`/expense/reports/${id}/approve`, data)
  },
  
  // 删除费用报销
  deleteExpenseReport(id) {
    return axios.delete(`/expense/reports/${id}`)
  },
  
  // 获取费用类型
  getExpenseTypes() {
    return axios.get('/expense/types')
  },
  
  // 获取费用统计
  getExpenseStatistics(params) {
    return axios.get('/expense/statistics', { params })
  }
}

// 工作日报API
export const diaryAPI = {
  // 获取工作日报列表
  getWorkDiaries(params) {
    return axios.get('/diary/diaries', { params })
  },
  
  // 创建工作日报
  createWorkDiary(data) {
    return axios.post('/diary/diaries', data)
  },
  
  // 获取工作日报详情
  getWorkDiary(id) {
    return axios.get(`/diary/diaries/${id}`)
  },
  
  // 更新工作日报
  updateWorkDiary(id, data) {
    return axios.put(`/diary/diaries/${id}`, data)
  },
  
  // 删除工作日报
  deleteWorkDiary(id) {
    return axios.delete(`/diary/diaries/${id}`)
  },
  
  // 获取今天的工作日报
  getTodayDiary() {
    return axios.get('/diary/today')
  },
  
  // 获取日报统计
  getDiaryStatistics(params) {
    return axios.get('/diary/statistics', { params })
  }
}

// 外出报备API
export const outingAPI = {
  // 获取外出报备列表
  getOutingReports(params) {
    return axios.get('/outing/reports', { params })
  },
  
  // 创建外出报备
  createOutingReport(data) {
    return axios.post('/outing/reports', data)
  },
  
  // 获取外出报备详情
  getOutingReport(id) {
    return axios.get(`/outing/reports/${id}`)
  },
  
  // 更新外出报备
  updateOutingReport(id, data) {
    return axios.put(`/outing/reports/${id}`, data)
  },
  
  // 审批外出报备
  approveOutingReport(id, data) {
    return axios.post(`/outing/reports/${id}/approve`, data)
  },
  
  // 完成外出报备
  completeOutingReport(id) {
    return axios.post(`/outing/reports/${id}/complete`)
  },
  
  // 删除外出报备
  deleteOutingReport(id) {
    return axios.delete(`/outing/reports/${id}`)
  },
  
  // 获取当前外出报备
  getCurrentOuting() {
    return axios.get('/outing/current')
  }
}

// 排班API
export const scheduleAPI = {
  // 获取排班列表
  getSchedules(params) {
    return axios.get('/schedule/schedules', { params })
  },
  
  // 创建排班
  createSchedule(data) {
    return axios.post('/schedule/schedules', data)
  },
  
  // 获取排班详情
  getSchedule(id) {
    return axios.get(`/schedule/schedules/${id}`)
  },
  
  // 更新排班
  updateSchedule(id, data) {
    return axios.put(`/schedule/schedules/${id}`, data)
  },
  
  // 删除排班
  deleteSchedule(id) {
    return axios.delete(`/schedule/schedules/${id}`)
  },
  
  // 获取我的排班
  getMySchedule(params) {
    return axios.get('/schedule/my-schedule', { params })
  },
  
  // 获取今天的排班
  getTodaySchedule() {
    return axios.get('/schedule/today')
  },
  
  // 获取班次类型
  getShiftTypes() {
    return axios.get('/schedule/shift-types')
  },
  
  // 获取排班日历
  getScheduleCalendar(params) {
    return axios.get('/schedule/calendar', { params })
  }
}

// 管理员API
export const adminAPI = {
  // 用户管理
  getUsers(params) {
    return axios.get('/admin/users', { params })
  },
  
  createUser(data) {
    return axios.post('/admin/users', data)
  },
  
  updateUser(id, data) {
    return axios.put(`/admin/users/${id}`, data)
  },
  
  deleteUser(id) {
    return axios.delete(`/admin/users/${id}`)
  },
  
  // 系统设置
  getSettings() {
    return axios.get('/admin/settings')
  },
  
  updateSettings(data) {
    return axios.post('/admin/settings', data)
  },
  
  // 考勤管理
  getAttendanceRecords(params) {
    return axios.get('/admin/attendance/records', { params })
  },
  
  getAttendanceStatistics(params) {
    return axios.get('/admin/attendance/statistics', { params })
  }
}

// 工具函数
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

export const formatDateTime = (datetime) => {
  return new Date(datetime).toLocaleString('zh-CN')
}

export const formatTime = (time) => {
  return new Date(`2000-01-01 ${time}`).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}