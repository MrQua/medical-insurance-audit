#!/bin/bash

# 医保智能审核系统启动脚本

echo "🏥 医保智能审核系统启动脚本"
echo "================================"

# 检查命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 未找到 $1，请先安装"
        exit 1
    fi
}

# 检查必要命令
check_command docker
check_command docker-compose

# 显示帮助
show_help() {
    echo "用法: ./start.sh [选项]"
    echo ""
    echo "选项:"
    echo "  all       启动所有服务（默认）"
    echo "  db        只启动数据库服务"
    echo "  backend   只启动后端服务（需要本地开发环境）"
    echo "  frontend  只启动前端服务（需要本地开发环境）"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  logs      查看服务日志"
    echo "  clean     清理数据（警告：会删除所有数据）"
    echo "  help      显示帮助"
}

# 启动所有服务
start_all() {
    echo "🚀 启动所有服务..."
    docker-compose up -d
    echo ""
    echo "✅ 服务启动完成！"
    echo "📱 前端界面: http://localhost:3000"
    echo "🔌 后端API: http://localhost:8000"
    echo "📚 API文档: http://localhost:8000/docs"
}

# 只启动数据库
start_db() {
    echo "🗄️ 启动数据库服务..."
    docker-compose up -d postgres qdrant
    echo "✅ 数据库服务已启动"
    echo "PostgreSQL: localhost:5432"
    echo "Qdrant: localhost:6333"
}

# 停止服务
stop_all() {
    echo "🛑 停止所有服务..."
    docker-compose down
    echo "✅ 服务已停止"
}

# 查看日志
show_logs() {
    docker-compose logs -f
}

# 清理数据
clean_data() {
    echo "⚠️  警告：这将删除所有数据！"
    read -p "确定要继续吗？(yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        docker-compose down -v
        rm -rf uploads/*
        echo "✅ 数据已清理"
    else
        echo "已取消"
    fi
}

# 主逻辑
case "${1:-all}" in
    all)
        start_all
        ;;
    db)
        start_db
        ;;
    backend)
        echo "📝 启动后端服务（本地模式）..."
        cd backend
        if command -v uv &> /dev/null; then
            uv pip install -r requirements.txt
        else
            pip install -r requirements.txt
        fi
        python -m uvicorn app.main:app --reload --port 8000
        ;;
    frontend)
        echo "💻 启动前端服务（本地模式）..."
        cd frontend
        npm install
        npm run dev
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_data
        ;;
    help|*)
        show_help
        ;;
esac
