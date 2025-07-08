#!/bin/bash

# 零售公司打卡系统启动脚本

echo "🚀 启动零售公司打卡系统..."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16 或更高版本"
    exit 1
fi

# 启动后端服务
echo "📱 启动后端服务..."
cd backend

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "🔧 创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装 Python 依赖
echo "📦 安装后端依赖..."
pip install -r requirements.txt

# 启动后端服务（后台运行）
echo "▶️  启动后端服务 (http://localhost:5000)..."
nohup python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端进程 PID: $BACKEND_PID"

# 返回项目根目录
cd ..

# 启动前端服务
echo "🖥️  启动前端服务..."
cd frontend

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端服务（后台运行）
echo "▶️  启动前端服务 (http://localhost:8080)..."
nohup npm run serve > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端进程 PID: $FRONTEND_PID"

# 返回项目根目录
cd ..

echo ""
echo "✅ 系统启动完成！"
echo ""
echo "📊 服务状态："
echo "   后端服务: http://localhost:5000 (PID: $BACKEND_PID)"
echo "   前端应用: http://localhost:8080 (PID: $FRONTEND_PID)"
echo ""
echo "👥 默认管理员账户："
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📋 管理命令："
echo "   查看后端日志: tail -f backend.log"
echo "   查看前端日志: tail -f frontend.log"
echo "   停止服务: ./stop.sh"
echo ""
echo "🌐 请在浏览器中访问: http://localhost:8080"

# 保存进程 PID 到文件
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# 等待几秒钟让服务完全启动
sleep 5

# 检查服务是否正常运行
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能未正常启动，请检查 backend.log"
fi

if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能未正常启动，请检查 frontend.log"
fi