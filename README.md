# 论文润色工具 (Paper Polish Tool)

AI驱动的论文润色与去AI化处理工具，基于智谱GLM-4大模型。

## 功能特点

- **论文润色**：支持学术严谨、自然流畅、正式规范三种风格
- **去AI化处理**：降低AI检测风险，提升文本自然度
- **实时进度**：处理过程可视化，状态一目了然
- **结果分析**：自然度评分、AI检测风险评估、改进建议

## 技术栈

### 后端
- Python 3.10+ / FastAPI
- SQLAlchemy / SQLite
- 智谱AI SDK (zhipuai)

### 前端
- React 18 + TypeScript
- Tailwind CSS
- Vite

### 部署
- Docker + Docker Compose
- Nginx 反向代理

## 快速开始

### 方式一：本地开发

1. 配置API密钥
```bash
# 编辑 backend/.env
ZHIPUAI_API_KEY=你的API密钥
```

2. 启动服务
```bash
# Windows
双击 启动服务.bat

# 或手动启动
cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

3. 访问 http://localhost:3000

### 方式二：Docker部署

```bash
docker-compose up -d
```

访问 http://localhost

## 项目优化

### 后端优化
- **异步处理**：所有AI调用和数据库操作均为异步
- **请求限流**：IP级别限流，防止滥用
- **LRU缓存**：缓存重复请求，减少API调用
- **自动重试**：AI调用失败自动重试3次
- **日志监控**：详细日志记录，支持性能追踪
- **智能模型选择**：根据文本长度自动选择模型

### 前端优化
- **错误重试**：网络错误自动重试
- **进度显示**：实时处理进度和状态
- **类型安全**：完整的TypeScript类型定义
- **响应式UI**：适配多种屏幕尺寸

### 安全优化
- **API Key保护**：仅在后端环境变量中配置
- **限流中间件**：防止API滥用
- **错误处理**：统一错误响应格式

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
│   │   ├── schemas/         # 数据结构
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具类
│   │       ├── cache.py     # LRU缓存
│   │       ├── limiter.py   # 请求限流
│   │       ├── logger.py    # 日志管理
│   │       └── retry.py     # 重试装饰器
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── hooks/           # 自定义Hooks
│   │   ├── services/        # API调用
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Docker编排
├── nginx/                   # Nginx配置
├── 启动服务.bat              # 本地启动
└── 上传到GitHub.bat          # Git上传
```

## API接口

### 润色接口
```
POST /api/polish/text
{
  "text": "需要润色的文本",
  "style": "academic|natural|formal",
  "ai_provider": "zhipuai"
}
```

### 去AI化接口
```
POST /api/anti-ai/process
{
  "text": "需要处理的文本",
  "ai_provider": "zhipuai"
}
```

### 统计接口
```
GET /stats
返回缓存和限流统计信息
```

## 许可证

MIT License

## 作者

cccyyywqq
