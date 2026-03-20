# 后端部署说明（uv 虚拟环境方式）

## 项目结构变化

```
backend/
├── app/                    # 应用代码
├── pyproject.toml          # 项目配置和依赖定义（替代 requirements.txt）
├── uv.lock                 # 依赖锁定文件（由 uv lock 生成）
├── Dockerfile              # 多阶段构建，使用 uv sync
├── run.sh / run.bat        # 本地开发启动脚本
└── DEPLOY.md               # 本文件
```

## 快速开始

### 1. 首次初始化

```bash
cd backend

# 生成 uv.lock 文件（只需执行一次）
uv lock

# 创建虚拟环境并安装依赖
uv sync --frozen
```

### 2. 本地开发

```bash
# 启动开发服务器（自动使用虚拟环境）
./run.sh          # Linux/Mac
run.bat           # Windows

# 或者手动使用 uv run
uv run uvicorn app.main:app --reload --port 8000
```

### 3. 常用命令

```bash
# 添加生产依赖
uv add fastapi

# 添加开发依赖
uv add --dev pytest

# 更新所有依赖
uv lock --upgrade
uv sync --frozen

# 运行代码检查
uv run ruff check app/
uv run black app/

# 运行测试
uv run pytest
```

## Docker 构建

### 多阶段构建说明

Dockerfile 包含三个阶段：

1. **builder**: 创建虚拟环境并安装依赖
2. **production** (默认): 精简的生产镜像，只包含虚拟环境和代码
3. **development**: 包含开发依赖和热重载

### 构建命令

```bash
# 构建生产镜像
docker build --target production -t medical-audit-backend .

# 构建开发镜像
docker build --target development -t medical-audit-backend:dev .

# 使用 Docker Compose 构建
docker-compose build backend
```

## 关键概念

### uv.lock 的作用

- 类似于 `package-lock.json` 或 `poetry.lock`
- 精确锁定每个依赖的版本和哈希值
- 确保团队所有成员和 CI/CD 使用完全相同的依赖
- **必须提交到版本控制！**

### 虚拟环境位置

- 本地开发: `backend/.venv/`
- Docker 容器: `/app/.venv/`

### 为什么使用 `uv run`?

- 自动检测并使用 `.venv` 中的 Python
- 无需手动激活虚拟环境
- 确保命令在正确的环境中运行

## 迁移指南（从 requirements.txt）

如果之前使用 pip + requirements.txt：

1. **删除旧文件**:
   ```bash
   rm requirements.txt
   ```

2. **安装新依赖**:
   ```bash
   uv lock
   uv sync
   ```

3. **更新 .gitignore**:
   ```gitignore
   # 旧的（如果使用）
   # venv/
   # env/

   # 新的（uv 使用 .venv，应该提交 uv.lock）
   .venv/          # 虚拟环境不提交
   !uv.lock        # 锁定文件要提交
   ```

## 故障排除

### uv.lock 冲突

```bash
# 重新生成锁定文件
rm uv.lock
uv lock
```

### 虚拟环境损坏

```bash
# 删除并重建
rm -rf .venv
uv sync
```

### Docker 构建缓存问题

```bash
# 无缓存构建
docker build --no-cache -t medical-audit-backend .
```

## 参考

- [uv 官方文档](https://docs.astral.sh/uv/)
- [PEP 621](https://peps.python.org/pep-0621/) - pyproject.toml 标准
