# 使用 uv 官方推荐的多阶段构建方式
FROM python:3.11-slim-bookworm AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /bin/uv

# 设置环境变量
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# 设置工作目录
WORKDIR /app

# 首先复制依赖定义文件（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖
# --frozen: 严格按照 uv.lock 安装，不更新 lock 文件
# --no-dev: 不安装开发依赖
# --no-install-project: 不安装项目本身，只安装依赖
RUN uv sync --frozen --no-dev --no-install-project

# ============================================
# 生产镜像（精简版）
FROM python:3.11-slim-bookworm AS production

# 设置工作目录
WORKDIR /app

# 从 builder 阶段复制虚拟环境
# 虚拟环境位于 /app/.venv
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY app/ ./app/

# 创建上传目录
RUN mkdir -p /app/uploads

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 使用虚拟环境的 Python 启动
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================
# 开发镜像（可选，包含开发依赖和工具）
FROM builder AS development

# 安装开发依赖
RUN uv sync --frozen

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# 开发模式使用热重载
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
