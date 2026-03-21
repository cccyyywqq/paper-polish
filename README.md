# 论文润色工具 (Paper Polish Tool)

[![Version](https://img.shields.io/badge/version-2.1.0-blue)](https://github.com/cccyyywqq/paper-polish)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com/)

AI驱动的论文润色与去AI化处理工具，基于智谱GLM-4大模型。

## 功能特点

| 功能 | 说明 |
|------|------|
| 📝 论文润色 | 学术严谨、自然流畅、正式规范三种风格 |
| 🤖 去AI化处理 | 降低AI检测风险，提升文本自然度 |
| 📁 文件上传 | 支持 .docx / .pdf / .txt 文件 |
| 👤 用户系统 | 登录注册、历史记录 |
| 📊 实时进度 | SSE 真实进度推送 |
| 🔍 对比视图 | 并排对比和段落对比两种模式 |

---

## 安装

### 环境要求

- Python 3.10+
- Node.js 18+
- 智谱AI API Key（[获取地址](https://open.bigmodel.cn/)）

### 克隆项目

```bash
git clone https://github.com/cccyyywqq/paper-polish.git
cd paper-polish
```

### 后端安装

```bash
cd backend
pip install -r requirements.txt
```

### 前端安装

```bash
cd frontend
npm install
```

---

## 配置

### 1. 复制配置文件

```bash
cd backend
cp .env.example .env
```

### 2. 编辑 `.env`

```env
# 环境配置
ENVIRONMENT=development
DEBUG=true

# AI服务配置 - 智谱GLM
ZHIPUAI_API_KEY=你的API密钥
ZHIPUAI_MODEL=glm-4-flash

# 认证安全配置
APP_SECRET_KEY=改成随机字符串
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS 配置 (生产环境改成你的域名)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 数据库配置
DATABASE_URL=sqlite:///./paper_polish.db
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 环境 (development/production) | development |
| `DEBUG` | 调试模式 | true |
| `ZHIPUAI_API_KEY` | 智谱AI API密钥 | - |
| `APP_SECRET_KEY` | 应用密钥（务必修改） | - |
| `CORS_ORIGINS` | 允许的前端域名 | localhost:3000 |
| `MAX_FILE_SIZE_MB` | 最大上传文件大小 | 10 |

---

## 启动

### 方式一：Windows 一键启动

双击 `启动服务.bat`

### 方式二：手动启动

**启动后端：**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**启动前端：**
```bash
cd frontend
npm run dev
```

### 方式三：Docker 启动

```bash
docker-compose up -d
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| API 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |
| 统计信息 | http://localhost:8000/stats |

---

## 架构

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy |
| 前端 | React 18 / TypeScript / Tailwind CSS |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| AI | 智谱GLM-4 API |
| 部署 | Docker / Nginx |

### 项目结构

```
paper-polish/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库配置
│   │   ├── models/              # 数据模型
│   │   ├── routers/             # API 路由
│   │   │   ├── polish.py        # 润色接口
│   │   │   ├── anti_ai.py       # 去AI化接口
│   │   │   ├── auth.py          # 用户认证
│   │   │   ├── upload.py        # 文件上传
│   │   │   └── progress.py      # SSE 进度
│   │   ├── schemas/             # Pydantic 模型
│   │   ├── services/            # 业务逻辑
│   │   │   ├── ai_service.py    # AI 服务
│   │   │   └── llm_client.py    # LLM 统一封装
│   │   └── utils/               # 工具类
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/          # React 组件
│   │   ├── services/            # API 调用
│   │   ├── hooks/               # 自定义 Hooks
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

### 核心流程

```
用户输入 → 前端验证 → API 请求 → 文本分段 → 并发调用 LLM → 结果合并 → 返回前端
    ↓                                                                    ↓
文件上传 → 解析提取 → 后端校验 → 10MB限制 → 格式验证 → 进入处理流程   SSE 进度推送
```

---

## API 接口

### 润色接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/polish/text | 润色文本 |
| POST | /api/polish/text-with-progress | 润色文本 (SSE进度) |
| POST | /api/polish/batch | 批量润色 |

### 去AI化接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/anti-ai/process | 去AI化处理 |
| POST | /api/anti-ai/analyze | 分析AI风险 |

### 用户接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 获取当前用户 |
| GET | /api/auth/history | 获取历史记录 |

### 系统接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /stats | 统计信息 |

---

## 测试

### Smoke Test 清单

按顺序执行以下步骤，验证核心功能：

#### 1. 注册
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"123456"}'
```
**预期**: 返回 `{"success":true, "id":1, ...}`

#### 2. 登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}'
```
**预期**: 返回 `{"success":true, "access_token":"eyJ..."}`

#### 3. 上传文件
```bash
echo "This is a test." > test.txt
curl -X POST http://localhost:8000/api/upload/file \
  -F "file=@test.txt"
```
**预期**: 返回 `{"success":true, "text":"This is a test.", ...}`

#### 4. 润色文本
```bash
curl -X POST http://localhost:8000/api/polish/text \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a test.","style":"academic"}'
```
**预期**: 返回 `{"success":true, "polished":"...", ...}`

#### 5. 健康检查
```bash
curl http://localhost:8000/health
```
**预期**: 返回 `{"status":"healthy", "checks":{...}}`

#### 6. 前端联调
1. 打开 http://localhost:3000
2. 点击"登录/注册"
3. 注册新用户
4. 登录
5. 输入文本，点击"开始处理"
6. 查看处理结果和进度

---

## 常见问题

### Q: 启动时报 "ZHIPUAI_API_KEY is not configured"
**A**: 检查 `backend/.env` 文件中是否正确配置了 `ZHIPUAI_API_KEY`

### Q: 前端无法连接后端
**A**: 
1. 确认后端已在 8000 端口启动
2. 检查 `CORS_ORIGINS` 是否包含前端地址
3. 检查防火墙设置

### Q: 文件上传失败
**A**: 
1. 检查文件大小是否超过 10MB
2. 确认文件格式为 .docx / .pdf / .txt
3. PDF 可能是扫描版，需要 OCR 处理

### Q: 润色请求超时
**A**: 
1. 检查网络连接
2. 确认智谱AI API Key 有效
3. 文本过长会自动分段处理，请耐心等待

### Q: 如何部署到生产环境
**A**: 
1. 修改 `.env` 中的 `ENVIRONMENT=production`
2. 设置强密码 `APP_SECRET_KEY`
3. 配置 `CORS_ORIGINS` 为你的域名
4. 使用 `docker-compose up -d` 启动

---

## 更新日志

### v2.1.0 (2024-03-21)
- 新增统一 LLM 调用封装层
- 添加 request_id 请求追踪
- 受控并发批处理
- 环境变量配置 CORS
- 完善 /health 和 /stats 接口

### v2.0.0 (2024-03-20)
- 新增用户系统（注册/登录/历史记录）
- 新增文件上传功能
- 新增 SSE 实时进度推送
- 新增对比视图
- 统一 API 响应格式
- 统一错误处理

### v1.0.0 (2024-03-19)
- 基础润色功能
- 去AI化处理
- 智谱GLM-4 集成

---

## 许可证

MIT License

## 作者

cccyyywqq

## 致谢

- [智谱AI](https://open.bigmodel.cn/) - GLM-4 大模型
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [React](https://react.dev/) - 前端框架
- [Tailwind CSS](https://tailwindcss.com/) - 样式框架
