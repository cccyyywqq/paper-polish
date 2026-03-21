# 论文润色工具 (Paper Polish Tool) v2.0.0

AI驱动的论文润色与去AI化处理工具，基于智谱GLM-4大模型。

## 功能特点

- **论文润色**：支持学术严谨、自然流畅、正式规范三种风格
- **去AI化处理**：降低AI检测风险，提升文本自然度
- **文件上传**：支持 .docx / .pdf / .txt 文件
- **用户系统**：登录注册、历史记录
- **实时进度**：SSE 真实进度推送
- **对比视图**：并排对比和段落对比两种模式

## 技术栈

### 后端
- Python 3.10+ / FastAPI
- SQLAlchemy / SQLite
- 智谱AI SDK (zhipuai)
- SSE (Server-Sent Events)

### 前端
- React 18 + TypeScript
- Tailwind CSS
- Vite + Axios

## 快速开始

### 1. 配置API密钥
编辑 `backend/.env`：
```
ZHIPUAI_API_KEY=你的智谱API密钥
SECRET_KEY=你的应用密钥
```

### 2. 启动服务
```bash
# Windows
双击 启动服务.bat

# 或手动启动
cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

### 3. 访问应用
- 前端：http://localhost:3000
- API文档：http://localhost:8000/docs

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
| POST | /api/auth/history | 保存历史记录 |

### 文件接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/file | 上传文件 |

### 进度接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/progress/stream/{task_id} | SSE进度流 |
| GET | /api/progress/status/{task_id} | 查询进度状态 |

## 项目结构

```
paper-polish/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI入口
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库配置
│   │   ├── models/          # 数据模型
│   │   ├── routers/         # API路由
│   │   │   ├── polish.py    # 润色接口
│   │   │   ├── anti_ai.py   # 去AI化接口
│   │   │   ├── auth.py      # 用户认证
│   │   │   ├── upload.py    # 文件上传
│   │   │   └── progress.py  # SSE进度
│   │   ├── schemas/         # Pydantic模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具类
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── services/        # API调用
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
├── 启动服务.bat
└── 上传到GitHub.bat
```

## 验收清单

- [x] 所有路由正确注册和导出
- [x] OpenAPI 文档包含全部接口
- [x] 前后端联调正常
- [x] SSE 进度推送正常
- [x] 文件上传功能正常
- [x] 用户认证功能正常
- [x] Docker 配置正确

## 许可证

MIT License

## 作者

cccyyywqq
