import streamlit as st
import pandas as pd
import google.generativeai as genai

# ตั้งชื่อแอป
st.set_page_config(page_title="Gemini Chat + CSV Upload", layout="wide")
st.title("🤖 Gemini Chat with CSV Upload")

# อัปโหลดไฟล์ CSV
st.header("📂 Upload Your CSV File")
try:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("✅ File successfully uploaded and read.")
        st.dataframe(st.session_state.uploaded_data.head())
except Exception as e:
    st.error(f"❌ Error while uploading file: {e}")

st.markdown("---")

# แชทกับ Gemini
st.header("💬 Chat with Gemini")

try:
    # โหลด API Key จาก secrets
    key = st.secrets["gemini_api_key"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    # เริ่มแชทใหม่หากยังไม่มีใน session
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    def role_to_streamlit(role: str) -> str:
        return "assistant" if role == "model" else role

    # แสดงประวัติการแชท
    for message in st.session_state.chat.history:
        with st.chat_message(role_to_streamlit(message.role)):
            for part in message.parts:
                st.markdown(part.text)

    # รับ prompt จากผู้ใช้
    if prompt := st.chat_input("Type your message here..."):
        st.chat_message("user").markdown(prompt)
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)

except Exception as e:
    st.error(f"❌ An error occurred while using Gemini: {e}")
