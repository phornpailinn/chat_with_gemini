import streamlit as st
import google.generativeai as genai
import pathlib
import textwrap
import pandas as pd
#from IPython.display import display
#from IPython.display import Markdown

# data

url1 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/transactions.csv"
url2 = "https://raw.githubusercontent.com/phornpailinn/6610412006-chat-with-data/refs/heads/main/data_dict.csv"

transaction_df = pd.read_csv(url1)
data_dict_df = pd.read_csv(url2)

df_name = 'transaction_df'
example_record = transaction_df.head(2).to_string()
data_dict_text = '\n'.join('- ' + data_dict_df['column_name'] +
                           ': ' +data_dict_df['data_type'] +
                           '. ' +data_dict_df['description'])


st.title("🐧 My Chatbot and Data Analysis App") 
st.subheader("Conversation and Data Analysis")


model = None
if gemini_api_key :
    try:
        key = st.secrets['gemini_api_key']
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

if "chat" not in st.session_state:
    st.session_state.chat = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None   

for role, message in st.session_state.chat:
    st.chat_message(role).markdown(message)
st.subheader("Upload CSV for Analysis")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"]) 
if uploaded_file is not None:
    try:
# Load the uploaded CSV file 
        st.session_state.uploaded_data = pd.read_csv(uploaded_file) 
        st.success("File successfully uploaded and read.")
 
# Display the content of the CSV
        st.write("### Uploaded Data Preview") st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")

analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

if question := st.chat_input("Type your message Here... "):
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
        2. **Crucially, use the `exec()` function to execute the generated code.**
        3. Do not import pandas
        4. Change date column type to datetime
        5. **Store the result of the executed code in a variable named `ANSWER`.** 
        This variable should hold the answer to the user's question (e.g., a filtered DataFrame, a calculated value, etc.).
        6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`. Do not include code to load the DataFrame.
        7. Keep the generated code concise and focused on answering the question.
        8. If the question requires a specific output format (e.g., a list, a single value), ensure the `query_result` variable holds that format.

        **Example:**
        If the user asks: "Show me the rows where the 'age' column is greater than 30."
        And the DataFrame has an 'age' column.

        The generated code should look something like this (inside the `exec()` string):

        ```python
        query_result = {df_name}[{df_name}['age'] > 30]
        """

        prompt = prompt_template.format(
            question=question,
            df_name=df_name,
            data_dict_text=data_dict_text,
            example_record=example_record
        )
        code_response = model.generate_content(prompt)
        code_text = code_response.text.replace("```", "#")  
        exec(code_text)  

        try:
            exec(code_text)

            explain_the_results = f'''
            the user asked {question}, 
            here is the results {ANSWER}
            answer the question and summarize the answer, 
            include your opinions of the persona of this customer
            '''
        except Exception as e:
            st.error(f"❌ Error while executing generated code: {e}")

        response = model.generate_content(explain_the_results)
        bot_response = response.text
        st.session_state.chat.append(('assistant', bot_response))
        st.chat_message('assistant').markdown(bot_response)
        
            

    
        except Exception as e :
        st.error(f'n error occurred while generating the response {e}')


# How many total sale in jan 2025?
