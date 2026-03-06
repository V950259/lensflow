import streamlit as st
import base64
import json
import time
from core.ai_client import LensAI
from core.logic_engine import LogicEngine

# --- Page Config ---
st.set_page_config(
    page_title="LensFlow - 全场景 AI 视觉助手",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Custom CSS ---
load_css("styles/main.css")

# --- Helper Functions ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/iris-scan.png", width=80)
    st.title("LensFlow")
    st.markdown("### ⚙️ 配置")
    
    # 默认使用智谱 API (根据用户之前的请求)
    api_key = st.text_input("API Key", value="9e546f3625334bfc9ea8a55036680de1.GtUkOzGH57D4IU3l", type="password")
    api_base = st.text_input("Base URL", value="https://open.bigmodel.cn/api/paas/v4/")
    model_name = st.text_input("模型名称", value="glm-4v")
    
    with st.expander("🔑 如何获取 API Key?"):
        st.markdown("""
        **1. 智谱 AI (推荐)**
        - [open.bigmodel.cn](https://open.bigmodel.cn/)
        - Model: `glm-4v`
        
        **2. OpenAI**
        - [platform.openai.com](https://platform.openai.com)
        - Model: `gpt-4o`
        """)
    st.markdown("---")
    
    # Reset Button
    if st.button("🔄 重置所有状态"):
        st.session_state.clear()
        st.rerun()

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_image_base64" not in st.session_state:
    st.session_state.current_image_base64 = None

# --- Initialize AI Client & Logic Engine ---
ai_client = LensAI(api_key=api_key, base_url=api_base, model_name=model_name)
logic_engine = LogicEngine()

# --- Main Interface ---
st.title("LensFlow - 全场景 AI 视觉助手")

# 1. Image Upload Section
upload_col, display_col = st.columns([1, 1])

with upload_col:
    with st.container(border=True):
        st.markdown("### 📤 上传")
        uploaded_file = st.file_uploader("选择图片", type=['jpg', 'png', 'jpeg'])
        camera_file = st.camera_input("或者拍一张")

target_file = uploaded_file if uploaded_file else camera_file

# Handle Image Logic
if target_file:
    # Convert to base64
    new_image_base64 = encode_image(target_file)
    
    # Check if it's a new image
    if new_image_base64 != st.session_state.current_image_base64:
        st.session_state.current_image_base64 = new_image_base64
        st.session_state.analysis_result = None
        st.session_state.messages = [] # Clear chat history for new image

    # Display Image
    with display_col:
        with st.container(border=True):
            st.markdown("### 🖼️ 预览")
            try:
                st.image(target_file, caption="当前图片", use_container_width=True)
            except TypeError:
                st.image(target_file, caption="当前图片", use_column_width=True)

    # 2. Vision Analysis Section
    if not st.session_state.analysis_result:
        if st.button("🔍 开始智能分析"):
            try:
                with st.status("🤖 LensAI 正在启动感知引擎...", expanded=True) as status:
                    st.write("👁️ 正在扫描图像视觉特征...")
                    time.sleep(0.8)  # 模拟扫描过程
                    
                    st.write("🧠 正在调用多模态大模型进行推理...")
                    result = ai_client.get_vision_response(st.session_state.current_image_base64)
                    
                    if result:
                        st.write("📂 正在解析场景数据与元信息...")
                        time.sleep(0.5)  # 模拟数据解析
                        
                        st.write("✨ 正在生成最终交互界面...")
                        time.sleep(0.3)
                        
                        st.session_state.analysis_result = result
                        # Initialize chat with context
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": "这是我上传的图片，请记住它。"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.current_image_base64}"}}
                            ]
                        })
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"好的，我已经分析了这张图片。它是 {result.get('title')}。{result.get('description')}"
                        })
                        status.update(label="✅ 分析完成！", state="complete", expanded=False)
                        st.rerun()
                    else:
                        status.update(label="❌ 分析失败", state="error")
            except Exception as e:
                st.error(f"发生错误: {e}")

# 3. Results & Chat Section
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    category = result.get("category")
    data = result.get("data", {})
    
    st.markdown("---")
    
    # --- Scene Card (Analysis Result) ---
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"## 🏷️ {result.get('title')}")
            st.caption(f"场景: {category}")
        with col2:
            st.write(result.get("description"))
            
            # Specific Data Display
            if category == "poster_notice":
                st.info(f"📅 **时间**: {data.get('time')} | 📍 **地点**: {data.get('location')}")
                st.success(f"📌 **活动**: {data.get('event_name')}")
                
                # Calendar Link Logic
                if data.get('time'):
                    cal_link = logic_engine.parse_calendar_data(
                        data.get('event_name', '活动'),
                        data.get('time'),
                        data.get('location', '')
                    )
                    if cal_link:
                        st.markdown(f"[📅 **添加到 Google Calendar**]({cal_link})")
                        
            elif category == "food_medicine":
                st.warning(f"⚠️ **风险提示**: {data.get('risk_warning')}")
                
                # Allergen Check Logic
                ingredients = data.get('ingredients', [])
                risks = logic_engine.analyze_health_risk(ingredients)
                if risks:
                    st.error(f"🚨 **严重警告**: 检测到潜在过敏原 - {', '.join(risks)}！")
                
                st.write(f"🧪 **成分**: {', '.join(ingredients)}")
            elif category == "general":
                st.info(f"📖 **百科**: {data.get('knowledge')}")

    # --- Chat Interface ---
    st.subheader("💬 智能对话")
    
    # Display chat history (skip the first hidden image context message for cleaner UI if desired, 
    # but for now we show all text interactions. We hide the raw image message to avoid clutter)
    for msg in st.session_state.messages:
        if msg["role"] == "user" and isinstance(msg["content"], list):
             # Skip displaying the initial image-setting message
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # User Input
    if prompt := st.chat_input("对这张图片还有什么疑问？(例如：这个活动是免费的吗？)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response_text = ai_client.get_chat_response(st.session_state.messages)
                st.write(response_text)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response_text})

elif not target_file:
    st.info("👋 请先上传图片开启体验")
