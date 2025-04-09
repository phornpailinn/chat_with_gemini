import streamlit as st
import pandas as pd
import google.generativeai as genai

# Title
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Conversation and Data Analysis")

# Set up Gemini API Key
gemini_api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="Paste your Gemini API key here...")
model = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(''gemini-1.5-flash'')
        st.success("✅ Gemini API Key configured.")
    except Exception as e:
        st.error(f"❌ Error setting up Gemini model: {e}")

# Load public CSV and data dictionary
url1 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/transactions.csv"
url2 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/data_dict.csv"

transaction_df = pd.read_csv(url1)
data_dict_df = pd.read_csv(url2)

df_name = 'transaction_df'
example_record = transaction_df.head(2).to_string()
data_dict_text = '\n'.join('- ' + data_dict_df['column_name'] + ': ' + data_dict_df['data_type'] + '. ' + data_dict_df['description'])

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# Chat History Display
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# File Uploader
st.subheader("📁 Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
if uploaded_file:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("📄 File uploaded and read successfully.")
        st.write("### 🧾 Uploaded Data Preview")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")

# Checkbox
analyze_data_checkbox = st.checkbox("📊 Analyze Uploaded CSV Data with AI")

# Chat Input
if user_input := st.chat_input("💬 Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                # Analyze uploaded data
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_summary = st.session_state.uploaded_data.describe().to_string()
                    prompt = f"Analyze the following dataset and provide insights:\n\n{data_summary}"
                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    # General prompt with uploaded data
                    prompt = f"The user says: {user_input}\n\nHere is a preview of the uploaded data:\n{st.session_state.uploaded_data.head().to_string()}"
                    response = model.generate_content(prompt)
                    bot_response = response.text

            else:
                # Use built-in dataset and Python code generation
                prompt_template = f"""
You are a helpful Python code generator. 
Your goal is to write Python code snippets based on the user's question 
and the provided DataFrame information.

Here's the context:

**User Question:**
{user_input}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question.
2. Use `exec()` to execute the code.
3. Do not import pandas.
4. Convert date columns to datetime if needed.
5. Store result in a variable named `ANSWER`.
6. Do not reload the DataFrame.
7. Keep code short and relevant.
"""
                code_response = model.generate_content(prompt_template)
                code_text = code_response.text.replace("```python", "").replace("```", "")
                try:
                    exec(code_text)
                    explain = f"The user asked: {user_input}\nHere is the result: {ANSWER}\nPlease summarize and provide any insights."
                    response = model.generate_content(explain)
                    bot_response = response.text
                    if isinstance(ANSWER, pd.DataFrame):
                        st.dataframe(ANSWER)
                    else:
                        st.write("📊 Result:", ANSWER)
                except Exception as e:
                    st.error(f"❌ Error while executing generated code: {e}")
                    bot_response = "⚠️ Failed to execute the generated code."

            # Display AI response
            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"❌ An error occurred while generating the response: {e}")
    else:
        st.warning("⚠️ Please provide a valid Gemini API key to start chatting.")
