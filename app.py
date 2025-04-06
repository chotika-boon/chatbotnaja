import pathlib
import textwrap
import pandas as pd
import streamlit as st
import google.generativeai as genai

# ---------------- Setup ----------------
genai.configure(api_key=st.secrets['gemini_api_key'])
model = genai.GenerativeModel('gemini-1.5-pro')
model1 = genai.GenerativeModel('gemini-1.5-pro')  # For explanation + persona

# ---------------- Load Data ----------------
df_name = "transaction_df"
transaction_df = pd.read_csv('transactions.csv')
example_record = transaction_df.head(2).to_string()

data_dict_df = pd.read_csv('data_dict.csv')
data_dict_text = '\n'.join(
    '- ' + row['column_name'] + ': ' + row['data_type'] + '. ' + row['description']
    for _, row in data_dict_df.iterrows()
)

# ---------------- Streamlit UI ----------------
st.title("📊 Ask Me About Your Data")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask me a data question...")

if user_input:
    question = user_input
    st.chat_message("user").markdown(question)

    # -------- Prompt for Code Generation --------
    prompt = f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question and the provided DataFrame information.

**User Question:**
{question}

**DataFrame Name:** {df_name}

**DataFrame Details:**
{data_dict_text}

**Sample Data (Top 2 Rows):**
{example_record}

**Instructions:**
1. Write Python code that answers the user's question.
2. Use `exec()` to execute the code.
3. Do NOT import pandas.
4. Convert the date column to datetime.
5. Store the result in a variable called `ANSWER`.
6. Assume the DataFrame is already loaded as `{df_name}`.
7. Keep the code concise and focused on answering the question.

**Example:**
For question: "Show me the rows where 'age' > 30", generate:
```python
query_result = {df_name}[{df_name}['age'] > 30]
"""
