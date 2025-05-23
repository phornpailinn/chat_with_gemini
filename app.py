import streamlit as st
import google.generativeai as genai
import pandas as pd

# โหลดข้อมูลจาก GitHub
url1 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/transactions.csv"
url2 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/data_dict.csv"

transaction_df = pd.read_csv(url1)
data_dict_df = pd.read_csv(url2)

df_name = 'transaction_df'
example_record = transaction_df.head(2).to_string()
data_dict_text = '\n'.join(
    '- ' + data_dict_df['column_name'] + ': ' + data_dict_df['data_type'] + '. ' + data_dict_df['description']
)

# UI Header
st.title("🐧 My Chatbot and Data Analysis App") 
st.subheader("Conversation and Data Analysis")

# Data Snapshot
st.markdown("## Data Description")
st.markdown("This dataset (CSV file) contains transaction data with the following columns:")
for index, row in data_dict_df.iterrows():
    st.markdown(f"**{row['column_name']}** ({row['data_type']}): {row['description']}")
st.markdown("### 🔍 Example Rows from Dataset:")
st.dataframe(transaction_df.head(5))

# Main Chatbot Section
try:
    key = st.secrets['gemini_api_key']
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    if "chat" not in st.session_state:
        st.session_state.chat = []

    def role_to_streamlit(role: str) -> str:
        return 'assistant' if role == 'model' else role

    for role, message in st.session_state.chat:
        st.chat_message(role_to_streamlit(role)).markdown(message)

    if question := st.chat_input("Ask Here"):
        st.session_state.chat.append(('user', question))
        st.chat_message('user').markdown(question)

        prompt_template = f"""
        You are a helpful Python code generator. 
        Your goal is to write Python code snippets based on the user's question 
        and the provided DataFrame information.

        Here's the context:

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
        This variable should hold the answer to the user's question (e.g., a filtered DataFrame, a calculated value, etc.).
        6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`. Do not include code to load the DataFrame.
        7. Keep the generated code concise and focused on answering the question.
        8. If the question requires a specific output format (e.g., a list, a single value), ensure the query_result variable holds that format.
        """

        prompt = prompt_template.format(
            question=question,
            df_name=df_name,
            data_dict_text=data_dict_text,
            example_record=example_record
        )
        code_response = model.generate_content(prompt)
        code_text = code_response.text.replace("```", "#")

        try:
            exec(code_text)
            explain_the_results = f'''
            the user asked: {question}
            here is the result: {ANSWER}
            answer the question and summarize the answer,
            include your opinions of the persona of this customer
            '''
            response = model.generate_content(explain_the_results)
            bot_response = response.text
            st.session_state.chat.append(('assistant', bot_response))
            st.chat_message('assistant').markdown(bot_response)
        except Exception as e:
            st.error(f"❌ Error while executing generated code: {e}")

except Exception as e:
    st.error(f'An error occurred: {e}')
