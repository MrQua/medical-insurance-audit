# 医保智能审核系统

基于规则引擎的医保收费违规智能审核系统，采用极简架构设计。

## 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端      │────▶│   后端      │────▶│  DeepSeek   │
│  (Vue3)     │◄────│  (FastAPI)  │◄────│   API       │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    │  (单一DB)   │
                    └─────────────┘
```

## 核心功能

1. **智能对话**
   - 流式输出响应
   - 基于 DeepSeek API 的多轮对话
   - 简单的助手问答功能

2. **患者管理**
   - 患者信息 CRUD
   - 收费项目管理
   - 统计信息展示

3. **违规审核（规则引擎）**
   - 基于 10 条简单规则的自动审核
   - 审核结果幂等性（重复审核覆盖旧结果）
   - 支持规则列表查看

4. **数据工厂**
   - 启动时自动初始化 10 个测试患者
   - 每个患者 100 条随机收费项目
   - 平均触发约 10 条规则

## 技术栈

### 后端
- **FastAPI** - Web 框架
- **PostgreSQL** - 关系数据库（单一数据源）
- **DeepSeek API** - 远程大模型服务
- **uv** - Python 虚拟环境和包管理

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端
- **Marked** - Markdown 渲染

## 快速开始

### 前置要求

1. Python 3.9+
2. Node.js 16+
3. PostgreSQL 数据库
4. DeepSeek API Key

### 配置

1. 创建环境变量文件：

```bash
cd backend
cp .env.example .env
```

2. 编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/medical_audit

# DeepSeek API 配置（必须）
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 其他配置
LOG_LEVEL=INFO
```

### 启动服务

**1. 启动数据库**

确保 PostgreSQL 已安装并运行，创建数据库：

```sql
CREATE DATABASE medical_audit;
```

**2. 启动后端**

```bash
cd backend

# 首次：安装 uv（如果尚未安装）
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 创建虚拟环境并安装依赖
uv sync

# 启动服务
uv run uvicorn app.main:app --reload --port 8000
```

**3. 启动前端**

```bash
cd frontend
npm install
npm run dev
```

### 访问系统

- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 使用说明

### 1. 智能对话

进入"智能对话"页面，直接与助手交流：
- 了解系统功能
- 查询医保相关政策
- 解释各类违规类型

### 2. 患者管理

进入"患者管理"页面：
- 系统已预置 10 个测试患者（各 100 条收费记录）
- 查看患者信息和收费项目
- 点击"审核"按钮执行规则审核

### 3. 审核规则

系统内置 10 条简单规则：

| 规则 | 说明 | 示例 |
|------|------|------|
| 前列腺检查性别限制 | 仅男性可开 | 女性开前列腺检查 → 违规 |
| 妇科检查性别限制 | 仅女性可开 | 男性开妇科检查 → 违规 |
| 儿童用药年龄限制 | 12岁以下限制 | 儿童用吗啡类药物 → 违规 |
| 老年人用药限制 | 65岁以上慎用 | 老人用氨基比林 → 违规 |
| CT检查金额限制 | 超过500元 | CT收费>500元 → 提示 |
| 高档药品审核 | 超过1000元 | 高价药 → 提示 |
| 进口材料审核 | 含"进口"字样 | 进口材料 → 提示 |
| 造影剂使用限制 | 含"造影/增强" | 造影检查 → 提示 |
| 抗生素使用审核 | 含抗生素类 | 抗生素 → 提示 |
| 重复检查提示 | CT/核磁/彩超 | 重复检查 → 提示 |

### 4. 审核幂等性

同一患者的重复审核会：
1. 先删除该患者所有旧的审核结果
2. 重新执行规则引擎
3. 插入新的审核结果

确保不会生成重复记录。

## API 接口

### 患者管理
- `GET /api/patients` - 获取患者列表
- `POST /api/patients` - 创建患者
- `GET /api/patients/{id}` - 获取患者详情
- `GET /api/patients/{id}/charges` - 获取患者收费项目
- `POST /api/patients/{id}/charges` - 添加收费项目

### 对话聊天
- `POST /api/chat` - 普通对话
- `POST /api/chat/stream` - 流式对话
- `GET /api/chat/history/{session_id}` - 获取聊天历史
- `GET /api/chat/sessions` - 获取会话列表

### 审核功能
- `POST /api/audit/patient/{id}` - 审核患者所有收费项目（幂等）
- `GET /api/audit/results/{charge_item_id}` - 获取审核结果
- `GET /api/audit/statistics` - 获取统计信息
- `GET /api/audit/rules` - 获取审核规则列表

## 项目结构

```
medical-insurance-audit/
├── backend/                # 后端代码
│   ├── app/
│   │   ├── models/        # 数据库模型
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务逻辑
│   │   │   ├── rule_engine.py    # 规则引擎
│   │   │   ├── audit_service.py  # 审核服务
│   │   │   └── deepseek_service.py # DeepSeek API 封装
│   │   ├── utils/         # 工具函数
│   │   ├── main.py        # 应用入口
│   │   └── config.py      # 配置
│   └── .env               # 环境变量
├── frontend/              # 前端代码
│   └── src/
│       ├── views/         # 页面组件
│       │   ├── Chat.vue   # 智能对话
│       │   ├── Patients.vue # 患者管理
│       │   └── Layout.vue   # 布局
│       ├── api/           # API 接口
│       └── router/        # 路由配置
└── README.md
```

## 数据模型

### 患者 (Patient)
- id: 患者ID
- name: 姓名
- age: 年龄
- gender: 性别
- id_card: 身份证号
- insurance_type: 医保类型

### 收费项目 (ChargeItem)
- id: 项目ID
- patient_id: 关联患者ID
- item_code: 项目编码
- item_name: 项目名称
- item_category: 项目类别（药品/检查/治疗/材料）
- quantity: 数量
- unit_price: 单价
- total_amount: 总金额
- charge_date: 收费日期

### 审核结果 (AuditResult)
- id: 结果ID
- charge_item_id: 关联收费项目ID
- is_violation: 是否违规
- violation_type: 违规类型
- violation_description: 违规描述
- suggestion: 处理建议
- rule_id: 触发的规则ID

### 审核规则 (AuditRule)
- id: 规则ID
- rule_name: 规则名称
- rule_type: 规则类型
- condition_field: 条件字段
- condition_operator: 条件操作符
- condition_value: 条件值
- violation_type: 违规类型

## 极简设计理念

本项目经过瘦身，移除了以下复杂组件：

| 移除组件 | 原用途 | 替代方案 |
|---------|--------|---------|
| Qdrant 向量库 | 文档向量化存储 | 直接使用规则引擎 |
| Sentence-Transformers | 本地嵌入模型 | 不使用向量检索 |
| Ollama 本地模型 | LLM 推理 | DeepSeek API |
| Dify 接口 | 知识库平台 | 直接使用 DeepSeek API |
| 知识库管理 | 文档上传/解析 | 删除该功能 |
| RAG 监控 | 检索过程监控 | 删除该功能 |

瘦身后的优势：
- **架构简单**：仅需 PostgreSQL + FastAPI + Vue3
- **部署方便**：无需向量数据库和本地大模型
- **维护容易**：规则引擎代码直观易懂
- **成本低**：按量使用 DeepSeek API

## 许可证

MIT License
