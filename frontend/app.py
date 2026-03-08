import streamlit as st
import base64
import time
import socket
import qrcode
import requests
import os
import pandas as pd
from io import BytesIO
from auth_ui import login_ui

# --- Configuration ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")

# --- Page Config ---
st.set_page_config(
    page_title="LensFlow - AI 视觉助手",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Custom CSS ---
load_css("styles/main.css")

# --- Helper Functions ---
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    return img_bytes

def get_local_ip():
    # Priority 1: Check environment variable (for Cloud/Docker deployment)
    public_url = os.getenv("PUBLIC_URL")
    if public_url:
        return public_url

    # Priority 2: Auto-detect local IP (for Localhost dev)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8501"
    except:
        return "http://127.0.0.1:8501"

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def show_scanning_animation():
    st.markdown("""
        <div class="scanning-overlay">
            <div class="scan-line"></div>
        </div>
    """, unsafe_allow_html=True)

def get_auth_headers():
    headers = {}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Add API Key if present in session state
    api_key = st.session_state.get("api_key")
    if api_key:
        headers["X-API-Key"] = api_key
        
    return headers

def api_chat_completions(messages):
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat/completions",
            json={"messages": messages},
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return response.json().get("response")
        return f"Error: {response.text}"
    except Exception as e:
        return f"API Error: {e}"

def api_check_risk(ingredients):
    try:
        response = requests.post(
            f"{BACKEND_URL}/logic/risk",
            json={"ingredients": ingredients},
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return response.json().get("risks", [])
        return []
    except Exception:
        return []

def api_get_calendar_link(event_name, time_str, location):
    try:
        response = requests.post(
            f"{BACKEND_URL}/logic/calendar/link",
            json={"event_name": event_name, "time_str": time_str, "location": location},
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return response.json().get("link")
        return None
    except Exception:
        return None

def api_get_ics_content(event_name, time_str, location):
    try:
        response = requests.post(
            f"{BACKEND_URL}/logic/calendar/ics",
            json={"event_name": event_name, "time_str": time_str, "location": location},
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            content = response.json().get("ics_content")
            return content.encode('utf-8') if content else None
        return None
    except Exception:
        return None

def api_get_profile():
    try:
        response = requests.get(f"{BACKEND_URL}/user/profile", headers=get_auth_headers())
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

def api_update_profile(medical_history, preferences):
    try:
        response = requests.put(
            f"{BACKEND_URL}/user/profile",
            json={"medical_history": medical_history, "preferences": preferences},
            headers=get_auth_headers()
        )
        return response.status_code == 200
    except Exception:
        return False

# --- Main App Logic ---
if "token" not in st.session_state:
    login_ui()
else:
    # --- Sidebar for Settings ---
    with st.sidebar:
        st.markdown("### ⚙️ 设置")
        
        # QR Code for Mobile Access
        mobile_url = get_local_ip()
        with st.popover("📲 在手机上打开"):
            st.image(generate_qr_code(mobile_url), caption="扫码在手机上体验", width=200)
            st.caption(f"访问地址: {mobile_url}")
            st.info("💡 如果部署在云端，请确保防火墙已开放端口")

        user_api_key = st.text_input("智谱 API Key (选填)", type="password", placeholder="填入以覆盖默认 Key")
        if user_api_key:
            st.session_state.api_key = user_api_key
        
        st.markdown("---")
        if st.button("注销"):
            del st.session_state["token"]
            st.rerun()

    # --- Authenticated View ---
    
    # Header
    col_h1, col_h2 = st.columns([8, 2])
    with col_h1:
        st.markdown(f"<h2 style='color: #343a40;'>LensFlow <span style='color: #007bff; font-size: 0.8em;'>测试版</span></h2>", unsafe_allow_html=True)

    # Tabs
    tab_scan, tab_history, tab_profile = st.tabs(["扫描", "历史记录", "个人中心"])

    # --- TAB 1: SCAN ---
    with tab_scan:
        col_upload, col_display = st.columns([1, 1])
        
        # State Init
        if "current_image_base64" not in st.session_state:
            st.session_state.current_image_base64 = None
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "messages" not in st.session_state:
            st.session_state.messages = []

        with col_upload:
            with st.container(border=True):
                uploaded_file = st.file_uploader("上传图片", type=['jpg', 'png', 'jpeg'])
                camera_file = st.camera_input("拍照")
                target_file = uploaded_file if uploaded_file else camera_file

        if target_file:
            # Process Image
            new_image_base64 = encode_image(target_file)
            if new_image_base64 != st.session_state.current_image_base64:
                st.session_state.current_image_base64 = new_image_base64
                st.session_state.analysis_result = None
                st.session_state.messages = [] # Reset chat for new image
            
            with col_display:
                with st.container(border=True):
                    # Use use_column_width for compatibility
                    st.image(target_file, use_column_width=True)

            # Analyze Button
            if st.button("开始智能分析", key="analyze_btn"):
                try:
                    show_scanning_animation()
                    with st.spinner("神经网络处理中..."):
                        response = requests.post(
                            f"{BACKEND_URL}/vision/analyze",
                            json={"image_base64": st.session_state.current_image_base64},
                            headers=get_auth_headers()
                        )
                        
                        if response.status_code == 200:
                            st.session_state.analysis_result = response.json()
                            
                            # Initialize chat context
                            result = st.session_state.analysis_result
                            st.session_state.messages = [
                                {
                                    "role": "user", 
                                    "content": [
                                        {"type": "text", "text": "这是我上传的图片，请记住它。"},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.current_image_base64}"}}
                                    ]
                                },
                                {
                                    "role": "assistant", 
                                    "content": f"好的，我已经分析了这张图片。它是 {result.get('title')}。{result.get('description')}"
                                }
                            ]
                            st.rerun()
                        else:
                            st.error(f"分析失败: {response.text}")
                except Exception as e:
                    st.error(f"发生错误: {e}")

        # Result Display
        if st.session_state.analysis_result:
            res = st.session_state.analysis_result
            category = res.get("category")
            data = res.get("data", {})
            
            st.markdown("---")
            
            # Perf Metrics
            if 'perf_report' in res:
                perf = res['perf_report']
                with st.expander("📊 性能数据", expanded=False):
                    cols = st.columns(4)
                    cols[0].metric("总延迟", f"{perf.get('total_latency', 0):.3f}s")
                    cols[1].metric("云端推理", f"{perf.get('cloud_inference_latency', 0):.3f}s")
                    cols[2].metric("本地预处理", f"{perf.get('local_preprocessing_latency', 0):.3f}s")
                    cols[3].metric("来源", "缓存" if perf.get('source') == 'cache' else "云端")

            # Content Card
            with st.container(border=True):
                st.markdown(f"## {res.get('title')}")
                st.caption(f"识别场景: {category.upper()}")
                st.info(res.get('description'))
                
                # --- Custom UI based on Category ---
                if category == "poster_notice":
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**📅 时间**: {data.get('time', '未识别')}")
                    with c2:
                        st.markdown(f"**📍 地点**: {data.get('location', '未识别')}")
                    
                    st.markdown(f"**📌 活动名称**: {data.get('event_name', '未识别')}")
                    
                    # Calendar Actions
                    if data.get('time'):
                        cal_link = api_get_calendar_link(data.get('event_name'), data.get('time'), data.get('location'))
                        ics_content = api_get_ics_content(data.get('event_name'), data.get('time'), data.get('location'))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if cal_link:
                                st.link_button("📅 添加到 Google Calendar", cal_link)
                        with col_btn2:
                            if ics_content:
                                st.download_button("⬇️ 下载 ICS 日历文件", data=ics_content, file_name="event.ics", mime="text/calendar")

                elif category == "food_medicine":
                    # Risk Warning
                    risk_warning = data.get('risk_warning')
                    if risk_warning:
                        st.error(f"⚠️ **风险提示**: {risk_warning}")
                    
                    # Ingredients
                    ingredients = data.get('ingredients', [])
                    if ingredients:
                        st.markdown("**🧪 成分**: " + ", ".join([f"`{i}`" for i in ingredients]))
                        # Check Risks
                        risks = api_check_risk(ingredients)
                        if risks:
                            for r in risks:
                                if r['severity'] == 'high':
                                    st.error(f"🚨 发现高危过敏原: **{r['allergen']}** ({r['warning']})")
                                else:
                                    st.warning(f"⚠️ 潜在风险: **{r['allergen']}**")
                    
                    # Specific Fields
                    if data.get('sub_category') == 'medicine':
                        st.info(f"💊 **用法用量**: {data.get('dosage_usage', '见说明书')}")
                    elif data.get('sub_category') == 'food':
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("🔥 热量", data.get('calories', 'N/A'))
                        with c2:
                            tags = data.get('health_tags', [])
                            if tags:
                                st.write("🏷️ " + " ".join([f"**{t}**" for t in tags]))
                
                elif category == "general":
                    st.markdown("### 📖 百科知识")
                    st.write(data.get('knowledge', '暂无详细信息'))
            
            # --- Chat Interface ---
            st.markdown("### 💬 智能对话")
            
            # Display chat history
            for msg in st.session_state.messages:
                if msg["role"] == "user" and isinstance(msg["content"], list):
                     # Skip displaying the initial image-setting message to keep UI clean
                    continue
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # User Input
            if prompt := st.chat_input("对这张图片还有什么疑问？"):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("思考中..."):
                        response_text = api_chat_completions(st.session_state.messages)
                        st.write(response_text)
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response_text})


    # --- TAB 2: HISTORY ---
    with tab_history:
        st.markdown("### 分析日志")
        
        # Export Buttons
        col_ex1, col_ex2, _ = st.columns([1, 1, 4])
        with col_ex1:
            try:
                pdf_res = requests.get(f"{BACKEND_URL}/report/pdf", headers=get_auth_headers())
                if pdf_res.status_code == 200:
                    st.download_button("下载 PDF 报告", data=pdf_res.content, file_name="report.pdf", mime="application/pdf")
            except:
                st.error("无法导出")
        
        with col_ex2:
            try:
                xlsx_res = requests.get(f"{BACKEND_URL}/report/excel", headers=get_auth_headers())
                if xlsx_res.status_code == 200:
                    st.download_button("下载 Excel 报表", data=xlsx_res.content, file_name="report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except:
                pass

        # Fetch History
        try:
            h_res = requests.get(f"{BACKEND_URL}/history", headers=get_auth_headers(), params={"limit": 20})
            if h_res.status_code == 200:
                history_data = h_res.json()
                if history_data:
                    for item in history_data:
                        with st.container(border=True):
                            c1, c2 = st.columns([1, 4])
                            c1.caption(item['timestamp'].split('T')[0])
                            c2.markdown(f"**{item['title']}** - _{item['category']}_")
                            c2.text(item['summary'])
                else:
                    st.info("暂无历史记录")
            else:
                st.error("无法加载历史记录")
        except Exception as e:
            st.error(f"连接错误: {e}")

    # --- TAB 3: PROFILE ---
    with tab_profile:
        st.markdown(f"### 用户: {st.session_state.username}")
        
        # Load existing profile
        profile = api_get_profile()
        current_medical = profile.get("medical_history", "") if profile else ""
        current_prefs = profile.get("preferences", "") if profile else ""

        with st.form("profile_form"):
            st.markdown("#### 🏥 健康档案与偏好")
            st.caption("LensFlow 将根据您的健康状况（如过敏史、慢性病）为您提供更精准的风险预警。")
            
            new_medical = st.text_area("病历/过敏史 (例如: 花生过敏, 糖尿病)", value=current_medical, height=100)
            new_prefs = st.text_area("个人偏好 (例如: 素食者, 正在减肥)", value=current_prefs, height=100)
            
            if st.form_submit_button("保存更新"):
                if api_update_profile(new_medical, new_prefs):
                    st.success("档案更新成功！下次扫描时生效。")
                    st.rerun()
                else:
                    st.error("更新失败，请重试。")
