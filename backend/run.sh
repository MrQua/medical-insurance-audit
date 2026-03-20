#!/bin/bash

# 医保智能审核系统 - 后端启动脚本（uv 虚拟环境方式）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 医保智能审核系统 - 后端启动脚本${NC}"
echo "======================================"

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ 未找到 uv，正在安装...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # 重新加载 PATH
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    echo -e "${GREEN}✅ uv 已安装: $(uv --version)${NC}"
}

# 初始化项目（首次运行）
init_project() {
    echo -e "${YELLOW}📦 初始化项目...${NC}"

    # 如果没有 uv.lock，生成它
    if [ ! -f "uv.lock" ]; then
        echo -e "${YELLOW}🔒 生成 uv.lock 文件...${NC}"
        uv lock
    fi

    # 创建虚拟环境并安装依赖
    echo -e "${YELLOW}📥 创建虚拟环境并安装依赖...${NC}"
    uv sync --frozen

    echo -e "${GREEN}✅ 项目初始化完成${NC}"
}

# 启动开发服务器
start_dev() {
    echo -e "${BLUE}🚀 启动开发服务器...${NC}"
    echo -e "${YELLOW}💡 提示: 使用 --reload 模式，代码修改会自动重启${NC}"
    echo ""

    # 使用 uv run 自动激活虚拟环境
    uv run uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info
}

# 启动生产服务器
start_prod() {
    echo -e "${BLUE}🚀 启动生产服务器...${NC}"

    uv run uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-level info
}

# 运行测试
run_tests() {
    echo -e "${BLUE}🧪 运行测试...${NC}"
    uv run pytest tests/ -v --tb=short
}

# 代码格式化
format_code() {
    echo -e "${BLUE}🎨 格式化代码...${NC}"
    uv run black app/
    uv run ruff check --fix app/
}

# 类型检查
type_check() {
    echo -e "${BLUE}🔍 类型检查...${NC}"
    uv run mypy app/
}

# 更新依赖
update_deps() {
    echo -e "${YELLOW}📦 更新依赖...${NC}"
    uv lock --upgrade
    uv sync --frozen
}

# 添加新依赖
add_dep() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ 请指定要安装的包名，例如: ./run.sh add requests${NC}"
        exit 1
    fi
    echo -e "${YELLOW}📦 添加依赖: $1${NC}"
    uv add "$1"
}

# 添加开发依赖
add_dev_dep() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ 请指定要安装的包名，例如: ./run.sh add-dev pytest${NC}"
        exit 1
    fi
    echo -e "${YELLOW}📦 添加开发依赖: $1${NC}"
    uv add --dev "$1"
}

# 激活虚拟环境（用于手动操作）
activate_venv() {
    echo -e "${BLUE}💡 虚拟环境激活命令:${NC}"
    echo "source .venv/bin/activate"
    echo ""
    echo -e "${YELLOW}或者使用 uv run 直接运行命令:${NC}"
    echo "uv run python script.py"
}

# 显示帮助
show_help() {
    echo "用法: ./run.sh [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  dev                启动开发服务器（默认）"
    echo "  prod               启动生产服务器"
    echo "  init               初始化项目（创建虚拟环境、安装依赖）"
    echo "  test               运行测试"
    echo "  format             格式化代码"
    echo "  lint               运行代码检查"
    echo "  type-check         运行类型检查"
    echo "  update             更新所有依赖"
    echo "  add <package>      添加生产依赖"
    echo "  add-dev <package>  添加开发依赖"
    echo "  activate           显示虚拟环境激活命令"
    echo "  help               显示帮助"
    echo ""
    echo "示例:"
    echo "  ./run.sh              # 启动开发服务器"
    echo "  ./run.sh init         # 首次初始化"
    echo "  ./run.sh add requests # 安装 requests 包"
}

# 主逻辑
cd "$(dirname "$0")"

case "${1:-dev}" in
    dev)
        check_uv
        if [ ! -d ".venv" ]; then
            init_project
        fi
        start_dev
        ;;
    prod)
        check_uv
        start_prod
        ;;
    init)
        check_uv
        init_project
        ;;
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    lint)
        uv run ruff check app/
        ;;
    type-check)
        type_check
        ;;
    update)
        update_deps
        ;;
    add)
        add_dep "$2"
        ;;
    add-dev)
        add_dev_dep "$2"
        ;;
    activate)
        activate_venv
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac
