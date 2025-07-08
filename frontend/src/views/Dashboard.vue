<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-card">
        <div class="welcome-info">
          <h2>欢迎回来，{{ currentUser?.real_name || '用户' }}！</h2>
          <p>{{ formatDate(new Date()) }} {{ getTimeGreeting() }}</p>
          <p class="department">{{ currentUser?.department || '' }} · {{ currentUser?.position || '' }}</p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="quickClockIn" :loading="clockInLoading">
            <el-icon><Clock /></el-icon>
            快速打卡
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card">
            <div class="stat-icon attendance">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ todayAttendance?.work_hours || 0 }}</div>
              <div class="stat-label">今日工时</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card">
            <div class="stat-icon leave">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pendingLeaveCount }}</div>
              <div class="stat-label">待审请假</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card">
            <div class="stat-icon expense">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ pendingExpenseCount }}</div>
              <div class="stat-label">待审报销</div>
            </div>
          </div>
        </el-col>
        
        <el-col :xs="12" :sm="6" :md="6" :lg="6">
          <div class="stat-card">
            <div class="stat-icon diary">
              <el-icon><EditPen /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ hasTodayDiary ? '已' : '未' }}</div>
              <div class="stat-label">今日日报</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20">
      <!-- 今日考勤 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>今日考勤</span>
              <el-button type="text" @click="$router.push('/attendance')">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="attendance-info">
            <div class="attendance-item">
              <div class="attendance-label">上班时间</div>
              <div class="attendance-value">
                {{ todayAttendance?.clock_in_time || '--:--' }}
              </div>
            </div>
            <div class="attendance-item">
              <div class="attendance-label">下班时间</div>
              <div class="attendance-value">
                {{ todayAttendance?.clock_out_time || '--:--' }}
              </div>
            </div>
            <div class="attendance-item">
              <div class="attendance-label">工作状态</div>
              <div class="attendance-value">
                <el-tag :type="getStatusType(todayAttendance?.status)">
                  {{ getStatusText(todayAttendance?.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 今日排班 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>今日排班</span>
              <el-button type="text" @click="$router.push('/schedule')">
                查看详情 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div v-if="todaySchedule" class="schedule-info">
            <div class="schedule-item">
              <div class="schedule-label">班次类型</div>
              <div class="schedule-value">
                <el-tag>{{ getShiftTypeText(todaySchedule.shift_type) }}</el-tag>
              </div>
            </div>
            <div class="schedule-item">
              <div class="schedule-label">工作时间</div>
              <div class="schedule-value">
                {{ todaySchedule.start_time }} - {{ todaySchedule.end_time }}
              </div>
            </div>
            <div v-if="todaySchedule.break_start" class="schedule-item">
              <div class="schedule-label">休息时间</div>
              <div class="schedule-value">
                {{ todaySchedule.break_start }} - {{ todaySchedule.break_end }}
              </div>
            </div>
          </div>
          <div v-else class="no-schedule">
            <el-empty description="今日无排班安排" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card class="content-card">
      <template #header>
        <span>快捷操作</span>
      </template>
      
      <div class="quick-actions">
        <div class="quick-action" @click="$router.push('/leave')">
          <div class="action-icon leave">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="action-text">请假申请</div>
        </div>
        
        <div class="quick-action" @click="$router.push('/expense')">
          <div class="action-icon expense">
            <el-icon><Money /></el-icon>
          </div>
          <div class="action-text">费用报销</div>
        </div>
        
        <div class="quick-action" @click="$router.push('/diary')">
          <div class="action-icon diary">
            <el-icon><EditPen /></el-icon>
          </div>
          <div class="action-text">工作日报</div>
        </div>
        
        <div class="quick-action" @click="$router.push('/outing')">
          <div class="action-icon outing">
            <el-icon><Position /></el-icon>
          </div>
          <div class="action-text">外出报备</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { Clock, Calendar, Money, EditPen, Position, ArrowRight } from '@element-plus/icons-vue'
import { attendanceAPI, scheduleAPI } from '../utils/api'

export default {
  name: 'Dashboard',
  components: {
    Clock, Calendar, Money, EditPen, Position, ArrowRight
  },
  setup() {
    const store = useStore()
    
    const todayAttendance = ref(null)
    const todaySchedule = ref(null)
    const clockInLoading = ref(false)
    const pendingLeaveCount = ref(0)
    const pendingExpenseCount = ref(0)
    const hasTodayDiary = ref(false)

    const currentUser = computed(() => store.getters.currentUser)

    const formatDate = (date) => {
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    }

    const getTimeGreeting = () => {
      const hour = new Date().getHours()
      if (hour < 12) return '上午好'
      if (hour < 18) return '下午好'
      return '晚上好'
    }

    const getStatusType = (status) => {
      const typeMap = {
        'normal': 'success',
        'late': 'warning',
        'early_leave': 'warning',
        'absent': 'danger'
      }
      return typeMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const textMap = {
        'normal': '正常',
        'late': '迟到',
        'early_leave': '早退',
        'absent': '缺勤',
        'not_clocked_in': '未打卡'
      }
      return textMap[status] || '未知'
    }

    const getShiftTypeText = (type) => {
      const typeMap = {
        'morning': '早班',
        'afternoon': '中班',
        'evening': '晚班',
        'night': '夜班'
      }
      return typeMap[type] || type
    }

    const loadTodayAttendance = async () => {
      try {
        const response = await attendanceAPI.getTodayAttendance()
        todayAttendance.value = response.data
      } catch (error) {
        console.error('获取今日考勤失败:', error)
      }
    }

    const loadTodaySchedule = async () => {
      try {
        const response = await scheduleAPI.getTodaySchedule()
        todaySchedule.value = response.data.schedule
      } catch (error) {
        console.error('获取今日排班失败:', error)
      }
    }

    const quickClockIn = async () => {
      try {
        clockInLoading.value = true
        
        if (todayAttendance.value?.clock_in_time && !todayAttendance.value?.clock_out_time) {
          // 下班打卡
          await attendanceAPI.clockOut()
          ElMessage.success('下班打卡成功')
        } else if (!todayAttendance.value?.clock_in_time) {
          // 上班打卡
          await attendanceAPI.clockIn()
          ElMessage.success('上班打卡成功')
        } else {
          ElMessage.info('今日已完成打卡')
          return
        }
        
        // 刷新考勤数据
        await loadTodayAttendance()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '打卡失败')
      } finally {
        clockInLoading.value = false
      }
    }

    onMounted(() => {
      loadTodayAttendance()
      loadTodaySchedule()
    })

    return {
      todayAttendance,
      todaySchedule,
      clockInLoading,
      pendingLeaveCount,
      pendingExpenseCount,
      hasTodayDiary,
      currentUser,
      formatDate,
      getTimeGreeting,
      getStatusType,
      getStatusText,
      getShiftTypeText,
      quickClockIn
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.welcome-section {
  margin-bottom: 24px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 30px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-info h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
}

.welcome-info p {
  margin: 4px 0;
  opacity: 0.9;
}

.department {
  font-size: 14px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: white;
}

.stat-icon.attendance {
  background: linear-gradient(45deg, #409eff, #66b3ff);
}

.stat-icon.leave {
  background: linear-gradient(45deg, #67c23a, #85ce61);
}

.stat-icon.expense {
  background: linear-gradient(45deg, #e6a23c, #f0c78a);
}

.stat-icon.diary {
  background: linear-gradient(45deg, #f56c6c, #f89898);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.content-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.attendance-info,
.schedule-info {
  space-y: 16px;
}

.attendance-item,
.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.attendance-item:last-child,
.schedule-item:last-child {
  border-bottom: none;
}

.attendance-label,
.schedule-label {
  font-weight: 500;
  color: #666;
}

.attendance-value,
.schedule-value {
  color: #333;
  font-weight: bold;
}

.no-schedule {
  text-align: center;
  padding: 40px 0;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #f0f0f0;
}

.quick-action:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 20px;
  color: white;
}

.action-icon.leave {
  background: linear-gradient(45deg, #67c23a, #85ce61);
}

.action-icon.expense {
  background: linear-gradient(45deg, #e6a23c, #f0c78a);
}

.action-icon.diary {
  background: linear-gradient(45deg, #f56c6c, #f89898);
}

.action-icon.outing {
  background: linear-gradient(45deg, #909399, #b1b3b8);
}

.action-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .welcome-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .welcome-info h2 {
    font-size: 20px;
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>