# 论文润色工具 (Paper Polish Tool)

AI驱动的论文润色与去AI化处理工具，基于智谱GLM-4大模型。

## 功能特点

- **论文润色**：支持学术严谨、自然流畅、正式规范三种风格
- **去AI化处理**：降低AI检测风险，提升文本自然度
- **实时进度**：处理过程可视化，状态一目了然
- **结果分析**：自然度评分、AI检测风险评估、改进建议

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy
- 智谱AI SDK (zhipuai)

### 前端
- React 18
- TypeScript
- Tailwind CSS
- Vite

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/cccyyywqq/paper-polish.git
cd paper-polish
```

### 2. 配置API密钥
编辑 `backend/.env` 文件，填入你的智谱AI API密钥：
```
ZHIPUAI_API_KEY=你的API密钥
```

### 3. 启动服务
双击 `启动服务.bat` 或手动执行：

**启动后端：**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**启动前端：**
```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用
- 前端页面：http://localhost:3000
- API文档：http://localhost:8000/docs

## 使用说明

1. 选择处理模式（论文润色 / 去AI化处理）
2. 选择润色风格（仅润色模式）
3. 粘贴需要处理的文本
4. 点击"开始处理"
5. 查看处理结果和分析报告

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
│   │   └── services/        # 业务逻辑
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── services/        # API调用
│   │   └── App.tsx
│   └── package.json
├── 启动服务.bat              # 一键启动
└── 上传到GitHub.bat          # 上传脚本
```

## 许可证

MIT License

## 作者

cccyyywqq
