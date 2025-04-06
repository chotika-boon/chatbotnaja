import streamlit as st
import google.generativeai as genai
import pandas as pd

# ---------------- Setup ----------------
genai.configure(api_key=st.secrets['gemini_api_key'])
model = genai.GenerativeModel('gemini-1.5-pro')  # ใช้รุ่นที่รองรับ context ยาว

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("your_transaction_file.csv")  # 👈 เปลี่ยนเป็นชื่อไฟล์ของคุณ
    return df

df = load_data()
df_name = "transaction_df"
data_dict_text = """
- invoice_and_item_number: STRING. Concatenated invoice and line number associated with the liquor order...
- date: DATE. Date of order
...
- sale_dollars: FLOAT64. Total cost of liquor ordered
"""  # 👈 ตัดมาแค่ตัวอย่าง ใส่ฉบับเต็มตามภาพ

example_record = df.head(2).to_markdown()

# ---------------- Prompt Builder ----------------
def build_prompt(user_question):
    return f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question and the provided DataFrame information.
Here’s the context:
**User Question:**  
{user_question}

**DataFrame Name:**  
{df_name}

**DataFrame Details:**  
{data_dict_text}

**Sample Data (Top 2 Rows):**  
{example_record}

**Instructions:**  
1. Write Python code that addresses the user’s question.
2. Critically, use the `exec()` function to execute the generated code.  
3. Do not import pandas.  
4. Change date column to datetime if needed.
5. Store the result in a variable named `ANSWER`.
    """.strip()

# ---------------- Streamlit UI ----------------
st.title("🧠 Gemini - Chat to Python Code")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask me a data question...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    prompt = build_prompt(user_input)

    with st.chat_message("assistant"):
        stream = model.generate_content(prompt, stream=True)
        full_response = ""
        response_placeholder = st.empty()
        for chunk in stream:
            if chunk.text:
                full_response += chunk.text
                response_placeholder.markdown(full_response)

        # -------- Execute Code --------
        local_scope = {df_name: df}
        try:
            exec(full_response, {}, local_scope)
            if "ANSWER" in local_scope:
                st.success("Query Result:")
                st.write(local_scope["ANSWER"])
            else:
                st.warning("No ANSWER variable returned.")
        except Exception as e:
            st.error(f"Error running code: {e}")
