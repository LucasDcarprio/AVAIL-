#!/bin/bash

# 零售公司打卡系统停止脚本

echo "🛑 停止零售公司打卡系统..."

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    echo "🔄 停止后端服务 (PID: $BACKEND_PID)..."
    
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    
    rm -f backend.pid
else
    echo "⚠️  未找到后端服务 PID 文件"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo "🔄 停止前端服务 (PID: $FRONTEND_PID)..."
    
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    
    rm -f frontend.pid
else
    echo "⚠️  未找到前端服务 PID 文件"
fi

# 清理可能残留的进程
echo "🧹 清理残留进程..."

# 查找并停止可能的 Flask 进程
FLASK_PIDS=$(pgrep -f "python.*app.py")
if [ ! -z "$FLASK_PIDS" ]; then
    echo "发现 Flask 进程: $FLASK_PIDS"
    echo $FLASK_PIDS | xargs kill
fi

# 查找并停止可能的 Vue 开发服务器进程
VUE_PIDS=$(pgrep -f "vue-cli-service serve")
if [ ! -z "$VUE_PIDS" ]; then
    echo "发现 Vue 进程: $VUE_PIDS"
    echo $VUE_PIDS | xargs kill
fi

echo ""
echo "✅ 系统已完全停止"
echo ""
echo "📋 相关文件："
echo "   后端日志: backend.log"
echo "   前端日志: frontend.log"
echo ""
echo "🔄 重新启动系统: ./start.sh"