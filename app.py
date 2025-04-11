import streamlit as st
import pandas as pd
import google.generativeai as genai

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Gemini Data Assistant", layout="wide")
st.title("🤖 Gemini Data Assistant + 📊 CSV Interpreter")

# ----------------------------
# API KEY SETUP
# ----------------------------
genai.configure(api_key=st.secrets["gemini_api_key"])
model = genai.GenerativeModel("gemini-1.5-pro")  # หรือใช้ "gemini-2.0-flash-lite"

# ----------------------------
# UPLOAD CSV
# ----------------------------
st.header("📂 Step 1: Upload Your CSV File")
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    # ----------------------------
    # ASK QUESTION OR WRITE CODE
    # ----------------------------
    st.markdown("---")
    st.header("❓ Step 2: Ask a Question or Write Python Code")
    question = st.text_input("🔎 Ask your question (e.g. What is the total sale in January 2025?)")

    use_custom_code = st.checkbox("🛠️ I want to write my own Python code instead of letting Gemini generate it")

    custom_code = ""
    if use_custom_code:
        custom_code = st.text_area(
            "✍️ Enter your custom Python code here (use variable `df`, assign result to `ANSWER`):",
            value="ANSWER = df.head()", height=200
        )

    # ----------------------------
    # PROCESS
    # ----------------------------
    if question or (use_custom_code and custom_code.strip()):
        df_name = "df"
        data_dict_text = str(dict(df.dtypes))
        example_record = df.head(2).to_dict()

        if not use_custom_code:
            # ----------------------------
            # GEMINI: GENERATE PYTHON CODE
            # ----------------------------
            prompt = f"""
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
4. Change date column type to datetime if needed
5. **Store the result of the executed code in a variable named `ANSWER`.**
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`.
7. Keep the generated code concise and focused on answering the question.
8. If the question requires a specific output format (e.g., a list, a single value), ensure the `ANSWER` variable holds that format.
"""

            with st.spinner("🧠 Generating Python code from Gemini..."):
                response = model.generate_content(prompt)
                generated_code = response.text.replace("```python", "").replace("```", "").strip()
        else:
            generated_code = custom_code

        # ----------------------------
        # EXECUTE CODE
        # ----------------------------
        st.subheader("🧪 Step 3: Generated or Custom Code")
        st.code(generated_code, language="python")

        try:
            local_vars = {"df": df}
            exec(generated_code, {}, local_vars)
            ANSWER = local_vars.get("ANSWER", "No ANSWER variable defined.")
            st.success("✅ Code executed successfully!")

            # ----------------------------
            # SHOW RESULT
            # ----------------------------
            st.subheader("📈 Step 4: Result")
            st.write(ANSWER)

            # ----------------------------
            # EXPLAIN RESULT
            # ----------------------------
            explain_prompt = f'''
The user asked: {question}
Here is the result: {ANSWER}

Please answer the question, summarize the result,
and optionally provide insights about the data or customer behavior.
'''

            with st.spinner("📋 Summarizing with Gemini..."):
                explanation = model.generate_content(explain_prompt)
                st.subheader("🧠 Gemini Explanation")
                st.markdown(explanation.text)

        except Exception as e:
            st.error(f"❌ Error while executing code: {e}")
