import streamlit as st
import pandas as pd
import google.generativeai as genai

# Set up the Streamlit app layout
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Conversation and Data Analysis")

# Initialize Gemini Model using Streamlit Secrets
try:
    key = st.secrets['gemini_api_key']
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    st.success("Gemini model successfully configured.")
except Exception as e:
    st.error(f"An error occurred while setting up the Gemini model: {e}")
    model = None

# Session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

if "uploaded_data_dict" not in st.session_state:
    st.session_state.uploaded_data_dict = None

# Display chat history
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# Upload CSV
st.subheader("Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("File successfully uploaded and read.")
        st.write("### Uploaded Data Preview")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

# Upload Data Dictionary
st.subheader("Upload Data Dictionary (Optional)")
uploaded_dict_file = st.file_uploader("Choose a Data Dictionary file", type=["csv"])
if uploaded_dict_file is not None:
    try:
        st.session_state.uploaded_data_dict = pd.read_csv(uploaded_dict_file)
        st.success("Data Dictionary file successfully uploaded and read.")
        st.write("### Data Dictionary Preview")
        st.dataframe(st.session_state.uploaded_data_dict.head())
    except Exception as e:
        st.error(f"An error occurred while reading the Data Dictionary: {e}")

# Enable data analysis
analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

# Chat + Analysis Logic
if question := st.chat_input("Ask Here"):
    st.session_state.chat_history.append(('user', question))
    st.chat_message('user').markdown(question)

    if model:
        try:
            df = st.session_state.uploaded_data
            if df is not None and analyze_data_checkbox and (
                "analyze" in question.lower()
                or "insight" in question.lower()
                or "how many" in question.lower()
                or "total" in question.lower()
            ):
                df_name = "df"
                data_dict_text = (
                    st.session_state.uploaded_data_dict.to_string()
                    if st.session_state.uploaded_data_dict is not None
                    else "No data dictionary provided."
                )

                # Convert potential date columns
                for col in df.columns:
                    if "date" in col.lower():
                        try:
                            df[col] = pd.to_datetime(df[col])
                        except:
                            pass

                example_record = df.head(2).to_string()

                prompt_template = f"""
You are a helpful Python code generator. 
Your goal is to write Python code snippets based on the user's question 
and the provided DataFrame information.

**User Question:**
{question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. **Crucially, use the exec() function to execute the generated code.**
3. Do not import pandas
4. Change date column type to datetime
5. **Store the result of the executed code in a variable named `ANSWER`.**
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`.
7. Keep the generated code concise and focused on answering the question.
"""

                prompt = prompt_template
                code_response = model.generate_content(prompt)
                code_text = code_response.text.replace("```", "#")

                try:
                    local_vars = {"df": df}
                    exec(code_text, {}, local_vars)
                    ANSWER = local_vars.get("ANSWER", "No result generated.")

                    explain_prompt = f"""
The user asked: "{question}".  
Here is the result: {ANSWER}  
Now summarize this result in a helpful way, and include your thoughts about the user's intent or persona if possible.
"""
                    final_response = model.generate_content(explain_prompt)
                    bot_response = final_response.text
                except Exception as e:
                    bot_response = f"❌ Error executing generated code: {e}"

                st.session_state.chat_history.append(('assistant', bot_response))
                st.chat_message('assistant').markdown(bot_response)

            elif not analyze_data_checkbox:
                msg = "✅ Chat received. But data analysis is disabled. Tick the checkbox above to enable it."
                st.session_state.chat_history.append(('assistant', msg))
                st.chat_message('assistant').markdown(msg)

            elif df is None:
                msg = "📄 Please upload a CSV file first, then ask me to analyze it."
                st.session_state.chat_history.append(('assistant', msg))
                st.chat_message('assistant').markdown(msg)

            else:
                response = model.generate_content(question)
                bot_response = response.text
                st.session_state.chat_history.append(('assistant', bot_response))
                st.chat_message('assistant').markdown(bot_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
