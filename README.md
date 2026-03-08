# LensFlow - 全场景 AI 视觉助手

Streamlit | FastAPI | Docker | Android (Jetpack Compose) | OpenAI

第十九届全国大学生软件创新大赛作品

LensFlow 是一款融合了多模态大模型感知与确定性逻辑引擎的智能视觉助手。它不只是简单地“看”图，更能深度理解场景，并连接现实世界的服务。

---

## 核心架构重构 (v2.0)

本项目已从单体脚本重构为前后端分离的微服务架构：

- **Frontend**: Streamlit (UI 展示与交互)
- **Backend**: FastAPI (核心 AI 逻辑、规则引擎、数据持久化)
- **Infrastructure**: Docker Compose (一键编排部署)
- **Mobile**: Android Native (可选 WebView 或 API 直连)

---

## 快速开始 (Docker 部署)

这是最推荐的运行方式，无需配置本地 Python 环境。

1. **配置环境变量**
   在根目录创建 `.env` 文件（可选，默认使用 `docker-compose.yml` 中的配置）：
   ```env
   API_KEY=your_api_key_here
   API_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
   MODEL_NAME=glm-4v
   ```

2. **一键启动**
   ```bash
   docker-compose up --build
   ```

3. **访问应用**
   - **Web 前端**: http://localhost:8501
   - **后端 API 文档**: http://localhost:8000/docs

---

## 项目结构

```
LensFlow/
├── backend/                # [后端] FastAPI 服务
│   ├── app/
│   │   ├── api/            # API 路由定义
│   │   ├── core/           # 核心业务逻辑 (AI, LogicEngine)
│   │   ├── models/         # Pydantic 数据模型
│   │   └── main.py         # 服务入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # [前端] Streamlit 界面
│   ├── app.py              # UI 主程序 (API Client)
│   ├── styles/             # CSS 样式
│   ├── Dockerfile
│   └── requirements.txt
├── data/                   # [数据] 持久化存储 (挂载卷)
│   ├── allergens.json      # 过敏原规则库
│   └── history.db          # 历史记录数据库
├── android-project/        # [移动端] Android 工程
├── docker-compose.yml      # 容器编排配置
└── README.md
```

## API 接口说明

后端服务暴露了以下核心 REST API，可供前端或移动端直接调用：

- `POST /api/v1/vision/analyze`: 上传图片 Base64，返回场景分析结果 JSON。
- `POST /api/v1/chat/completions`: 多轮对话接口。
- `POST /api/v1/logic/risk`: 传入成分列表，返回过敏风险分析。
- `POST /api/v1/logic/calendar/link`: 生成 Google Calendar 链接。
- `POST /api/v1/logic/calendar/ics`: 生成 .ics 日历文件内容。

---

## 开发指南

### 本地开发 (非 Docker)

**1. 启动后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. 启动前端**
```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL="http://localhost:8000/api/v1"  # Windows (PowerShell): $env:BACKEND_URL="http://localhost:8000/api/v1"
streamlit run app.py
```

---

Created with ❤️ for the 19th National Software Innovation Contest for College Students.
