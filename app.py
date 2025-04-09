import streamlit as st
import pandas as pd
import google.generativeai as genai

# UI ต้อนรับ
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Conversation and Data Analysis")

# กรอก API Key
gemini_api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="Paste your Gemini API key here...")

# โหลดโมเดล
model = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")
        st.success("✅ Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"❌ Error setting up Gemini model: {e}")

# เซสชัน state สำหรับแชทและข้อมูล
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# แสดงข้อความแชทก่อนหน้า
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# อัปโหลดไฟล์ CSV
st.subheader("📁 Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("📄 File uploaded and read successfully.")
        st.write("### 🧾 Uploaded Data Preview")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")

# Checkbox ให้ผู้ใช้เลือกวิเคราะห์ข้อมูล
analyze_data_checkbox = st.checkbox("📊 Analyze CSV Data with AI")

# อินพุตจากผู้ใช้
if user_input := st.chat_input("💬 Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                # ตรวจว่าผู้ใช้ต้องการวิเคราะห์ข้อมูลหรือไม่
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_description = st.session_state.uploaded_data.describe().to_string()

                    prompt = f"""
You are a data analyst AI.
Here is the statistical summary of a dataset:

{data_description}

Please analyze this and provide insights, trends, and any potential patterns found in the dataset.
"""

                    response = model.generate_content(prompt)
                    bot_response = response.text

                else:
                    # คำถามทั่วไป
                    response = model.generate_content(user_input)
                    bot_response = response.text

            elif not analyze_data_checkbox:
                bot_response = "🕹️ Data analysis is disabled. Please check the box above to enable it."

            else:
                bot_response = "📂 Please upload a CSV file first."

            # แสดงผล AI
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"❌ An error occurred during response generation: {e}")
    else:
        st.warning("⚠️ Please enter your Gemini API key above.")
