# 零售公司打卡系统

基于 Python Flask 和 Vue.js 构建的现代化企业考勤管理系统，专为零售公司设计，具备完整的打卡、请假、报销、日报等功能。

## 🚀 功能特性

### 核心功能
- **考勤打卡**: 支持上下班打卡，自动记录工作时长
- **IP地址限制**: 只能在店内指定IP地址进行打卡
- **请假申请**: 完整的请假申请、审批流程
- **费用报销**: 费用报销申请和审批管理
- **工作日报**: 员工日常工作记录和汇报
- **外出报备**: 外出工作的申请和管理
- **排班查看**: 员工排班安排和查询

### 管理功能
- **用户管理**: 员工信息管理和权限控制
- **系统设置**: 工作时间、休息时间等参数配置
- **数据统计**: 考勤统计、费用统计等报表功能
- **权限管理**: 管理员、经理、员工三级权限体系

### 技术特性
- **现代化UI**: 基于Element Plus的美观界面
- **响应式设计**: 支持桌面端和移动端访问
- **安全认证**: JWT Token身份验证
- **数据持久化**: SQLite/MySQL数据库支持
- **API接口**: RESTful API设计

## 🛠️ 技术栈

### 后端
- **Python 3.8+**
- **Flask** - Web框架
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT认证
- **Flask-CORS** - 跨域支持
- **SQLite/MySQL** - 数据库

### 前端
- **Vue 3** - 前端框架
- **Vue Router** - 路由管理
- **Vuex** - 状态管理
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端

## 📦 安装部署

### 环境要求
- Python 3.8 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

### 后端部署

1. **克隆项目**
```bash
git clone <your-repo-url>
cd attendance-system
```

2. **创建虚拟环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和密钥
```

5. **初始化数据库**
```bash
python app.py
```

6. **启动后端服务**
```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动

### 前端部署

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
# 或
yarn install
```

3. **启动开发服务器**
```bash
npm run serve
# 或
yarn serve
```

前端应用将在 `http://localhost:8080` 启动

## 👥 默认账户

系统启动后会自动创建管理员账户：
- **用户名**: admin
- **密码**: admin123
- **角色**: 管理员

## 📖 使用指南

### 员工操作

1. **注册登录**
   - 新员工可以通过注册页面创建账户
   - 使用用户名和密码登录系统

2. **考勤打卡**
   - 进入考勤页面进行上下班打卡
   - 系统会验证IP地址，确保在店内打卡
   - 自动计算工作时长和考勤状态

3. **请假申请**
   - 提交请假申请，选择请假类型和时间
   - 等待管理员审批
   - 查看申请状态和历史记录

4. **费用报销**
   - 提交各类费用报销申请
   - 上传相关凭证（可选）
   - 跟踪报销进度

5. **工作日报**
   - 每日提交工作总结
   - 记录工作成果、问题和计划
   - 查看历史日报

6. **外出报备**
   - 外出工作前提交报备申请
   - 记录外出目的、地点和时间
   - 返回后确认完成

### 管理员操作

1. **用户管理**
   - 查看所有员工信息
   - 创建、编辑、删除员工账户
   - 设置员工权限和部门

2. **系统设置**
   - 配置工作时间（上班、下班、休息时间）
   - 设置允许打卡的IP地址范围
   - 其他系统参数配置

3. **考勤管理**
   - 查看所有员工考勤记录
   - 生成考勤统计报告
   - 处理考勤异常

4. **审批管理**
   - 审批员工请假申请
   - 处理费用报销申请
   - 审核外出报备申请

5. **排班管理**
   - 创建和管理员工排班表
   - 设置不同班次时间
   - 查看排班日历

## ⚙️ 配置说明

### 环境变量配置

在 `backend/.env` 文件中配置以下参数：

```env
# Flask配置
SECRET_KEY=your-secret-key-for-flask-sessions
JWT_SECRET_KEY=your-jwt-secret-key-for-tokens
FLASK_ENV=development
FLASK_DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///attendance.db
# 或使用MySQL
# DATABASE_URL=mysql+pymysql://username:password@localhost/attendance_db
```

### 系统设置

管理员可以在系统设置页面配置：

- **工作时间设置**
  - work_start_time: 上班时间 (默认: 09:00)
  - work_end_time: 下班时间 (默认: 18:00)
  - break_duration: 休息时长（小时） (默认: 1.0)

- **IP地址限制**
  - allowed_ips: 允许打卡的IP地址列表 (例如: 192.168.1.0/24,10.0.0.1)

## 🔧 开发指南

### 项目结构

```
attendance-system/
├── backend/                 # 后端Flask应用
│   ├── app.py              # 应用入口
│   ├── models.py           # 数据模型
│   ├── routes/             # 路由模块
│   │   ├── auth.py         # 认证相关
│   │   ├── attendance.py   # 考勤相关
│   │   ├── leave.py        # 请假相关
│   │   ├── expense.py      # 报销相关
│   │   ├── diary.py        # 日报相关
│   │   ├── outing.py       # 外出相关
│   │   ├── schedule.py     # 排班相关
│   │   └── admin.py        # 管理功能
│   ├── requirements.txt    # Python依赖
│   └── .env               # 环境配置
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── components/     # 通用组件
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── utils/          # 工具函数
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
└── README.md               # 项目说明
```

### API接口

后端提供完整的RESTful API接口，主要包括：

- `/api/auth/*` - 认证相关接口
- `/api/attendance/*` - 考勤相关接口
- `/api/leave/*` - 请假相关接口
- `/api/expense/*` - 报销相关接口
- `/api/diary/*` - 日报相关接口
- `/api/outing/*` - 外出相关接口
- `/api/schedule/*` - 排班相关接口
- `/api/admin/*` - 管理功能接口

### 开发规范

1. **代码风格**
   - Python: 遵循PEP8规范
   - JavaScript: 使用ES6+语法
   - Vue: 遵循Vue.js官方风格指南

2. **API设计**
   - 使用RESTful设计原则
   - 统一的错误处理和响应格式
   - 完整的参数验证

3. **数据库设计**
   - 使用SQLAlchemy ORM
   - 合理的表结构和索引设计
   - 数据迁移脚本

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置是否正确
   - 确认数据库服务是否启动
   - 验证连接字符串格式

2. **前端无法连接后端**
   - 检查后端服务是否启动
   - 确认API地址配置正确
   - 检查CORS设置

3. **打卡IP验证失败**
   - 确认IP地址配置正确
   - 检查网络环境
   - 验证IP地址格式

4. **JWT Token过期**
   - 检查Token有效期设置
   - 确认时间同步
   - 清除本地存储重新登录

### 日志调试

- 后端日志：查看Flask应用输出
- 前端日志：打开浏览器开发者工具
- 数据库日志：检查数据库查询和错误

## 📝 License

本项目采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 📞 联系方式

如有问题或建议，请联系项目维护者。
