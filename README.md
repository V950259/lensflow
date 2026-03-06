# LensFlow - 全场景 AI 视觉助手 👁️

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **第十九届全国大学生软件创新大赛作品**

**LensFlow** 是一款融合了**多模态大模型感知**与**确定性逻辑引擎**的智能视觉助手。它不只是简单地“看”图，更能深度理解场景，并连接现实世界的服务。

无论是会议海报、药品说明书还是日常生活用品，LensFlow 都能通过**可视化思维链**展示分析过程，并提供一键日历添加、健康风险预警等实用功能。

---

## ✨ 核心亮点

### 1. 👁️ 可视化感知引擎
告别枯燥的 Loading 圈！LensFlow 引入了**全链路思维可视化**交互：
*   **视觉扫描**: 模拟光感扫描过程。
*   **模型推理**: 展示多模态大模型的思考状态。
*   **数据解析**: 实时呈现非结构化数据到结构化信息的转化。
*   **界面生成**: 动态构建场景化 UI。

### 2. 🧠 "AI + 规则" 双引擎架构
*   **LensAI (概率层)**: 基于 GPT-4o / GLM-4v 等顶尖多模态模型，负责对非结构化图像进行泛化理解和语义提取。
*   **LogicEngine (确定层)**: 内置业务规则引擎，负责处理高精度的确定性任务：
    *   **过敏原风控**: 针对食品/药品成分，匹配本地过敏原库（如花生、海鲜），提供**零容忍**的红色警示。
    *   **日历协议生成**: 自动解析时间并生成 Google Calendar 标准 URL Scheme。

### 3. 💬 场景化多轮对话
*   **上下文记忆**: AI 能够记住当前的图片内容，您随时可以追问（例如：“这张海报里的嘉宾也是上次那个活动的吗？”）。
*   **图文混合理解**: 完美融合视觉信息与文本语境。

---

## 📱 场景演示

| 场景类型 | 识别内容 | 智能服务 |
| :--- | :--- | :--- |
| **📅 海报/通知** | 会议海报、活动传单 | ✅ **提取关键要素** (时间/地点/人物)<br>✅ **生成日历链接** (一键添加到日程) |
| **💊 食品/药品** | 药盒包装、零食配料表 | ✅ **成分深度分析**<br>✅ **🚨 健康风险预警** (自动检测过敏原) |
| **📖 万物百科** | 花草、宠物、电子产品 | ✅ **百科知识科普**<br>✅ **相关性推荐** |

---

## 🛠️ 技术架构

LensFlow 采用高内聚、低耦合的模块化设计：

```mermaid
graph TD
    User[用户] --> Frontend[Streamlit 前端 (app.py)]
    Frontend --> AI[AI Client (core/ai_client.py)]
    Frontend --> Logic[Logic Engine (core/logic_engine.py)]
    
    AI -->|图像+Prompt| LLM[多模态大模型 API]
    LLM -->|JSON 数据| AI
    
    Logic -->|提取时间| Calendar[日历链接生成器]
    Logic -->|提取成分| Risk[过敏原匹配算法]
    
    Frontend -->|展示| UI[场景化卡片 UI]
```

*   **app.py**: 负责 UI 渲染、Session 状态管理 (`st.session_state`) 及全链路控制。
*   **core/ai_client.py**: 封装 OpenAI 格式接口，实现图像 Base64 编码及 System Prompt 注入。
*   **core/logic_engine.py**: 纯 Python 实现的业务逻辑层，不依赖外部 AI，保证核心业务（如报警）的稳定性。

---

## 🚀 快速开始

### 1. 环境准备
确保您的电脑上安装了 Python 3.8+。

```bash
# 克隆项目
git clone <your-repo-url>
cd LensFlow

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用
```bash
streamlit run app.py
```

### 3. 配置使用
1.  系统会自动打开浏览器访问 `http://localhost:8501`。
2.  在侧边栏配置您的 API Key（支持 OpenAI、智谱 GLM-4v 等兼容接口）。
3.  点击相机图标或上传图片，观察**可视化思维链**的运行过程！

---

## 🌐 在线部署 (Deployment)

本项目完全适配 **Streamlit Community Cloud**，可实现**零配置一键部署**。

### 部署步骤
1.  **上传代码到 GitHub**: 将本项目推送到您的 GitHub 仓库。
2.  **访问 Streamlit Cloud**: 登录 [share.streamlit.io](https://share.streamlit.io/)。
3.  **新建应用 (New App)**:
    *   Repository: 选择您的 `LensFlow` 仓库。
    *   Branch: `main` (或 `master`)。
    *   Main file path: `app.py`。
4.  **点击 Deploy**: 等待几分钟，您将获得一个永久的 HTTPS 访问链接（例如 `https://lensflow.streamlit.app`）。

> **注意**: 部署后，请在 Streamlit Cloud 的 "Advanced Settings" -> "Secrets" 中配置您的 API Key，或者直接在网页侧边栏输入。

---

## 📂 项目结构

```
LensFlow/
├── app.py              # 🚀 应用主入口 (UI与交互逻辑)
├── core/               # 🧠 核心算法层
│   ├── ai_client.py    #    - AI 模型接口封装
│   └── logic_engine.py #    - 业务规则与数据处理引擎
├── styles/             # 🎨 资源层
│   └── main.css        #    - 全局自定义样式
├── requirements.txt    # 📦 依赖清单
└── README.md           # 📄 说明文档
```

---

*Created with ❤️ for the 19th National Software Innovation Contest for College Students.*
