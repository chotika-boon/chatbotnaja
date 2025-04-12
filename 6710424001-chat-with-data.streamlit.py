import streamlit as st
import pandas as pd
import google.generativeai as genai

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Gemini CSV Analyst", layout="wide")
st.title("📊 Gemini Data Assistant + Excel Dictionary Interpreter")

# ----------------------------
# SETUP API
# ----------------------------
genai.configure(api_key=st.secrets["gemini_api_key"])
model = genai.GenerativeModel("gemini-1.5-pro")

# ----------------------------
# UPLOAD 2 FILES
# ----------------------------
st.header("📂 Step 1: Upload Your Files")

col1, col2 = st.columns(2)
with col1:
    data_file = st.file_uploader("🧾 Upload your **main data file** (CSV)", type="csv", key="data")
with col2:
    dict_file = st.file_uploader("📘 Upload your **data dictionary** (CSV)", type="csv", key="dict")

if data_file and dict_file:
    try:
        df = pd.read_csv(data_file)
        data_dict = pd.read_csv(dict_file)

        st.success("✅ Files uploaded successfully!")
        st.subheader("🔍 Preview Data")
        st.dataframe(df.head())

        st.subheader("📘 Data Dictionary")
        st.dataframe(data_dict)

        # ----------------------------
        # CONVERT DICTIONARY TO TEXT
        # ----------------------------
        dict_text = "\n".join([
            f"- **{row['column']}**: {row['description']}"
            for _, row in data_dict.iterrows() if 'column' in row and 'description' in row
        ])

        # ----------------------------
        # USER INPUTS
        # ----------------------------
        st.markdown("---")
        st.header("❓ Step 2: Ask a Question or Write Python Code")
        question = st.text_input("🔎 What do you want to know about the data?")

        use_custom_code = st.checkbox("🛠️ I want to write my own Python code")

        custom_code = ""
        if use_custom_code:
            custom_code = st.text_area(
                "✍️ Enter Python code using `df`, store result in `ANSWER`:",
                value="ANSWER = df['amount'].sum()  # ตัวอย่าง: ยอดรวมทั้งหมด",
                height=180
            )

        # ----------------------------
        # IF READY TO PROCESS
        # ----------------------------
        if question or (use_custom_code and custom_code.strip()):
            df_name = "df"
            col_types = df.dtypes.astype(str).to_dict()
            sample_rows = df.head(1).to_dict()

            if not use_custom_code:
                prompt = f"""
You are a Python code generator that answers questions by working with a Pandas DataFrame.

**User Question:**  
{question}

**DataFrame Name:** `{df_name}`  
**Column Types:**  
{col_types}  

**Sample Record:**  
{sample_rows}

**Data Dictionary:**  
{dict_text}

**Instructions:**
- Do not import pandas.
- Use DataFrame `{df_name}` as your working data.
- Convert date columns with `pd.to_datetime()` if needed.
- Store the final result in variable `ANSWER`.
- If needed, filter, group, or summarize.
- Do not add print().
- Your answer must be valid Python inside `exec()`.
"""

                with st.spinner("🧠 Generating code with Gemini..."):
                    response = model.generate_content(prompt)
                    generated_code = response.text.replace("```python", "").replace("```", "").strip()
            else:
                generated_code = custom_code

            # ----------------------------
            # EXECUTE GENERATED OR CUSTOM CODE
            # ----------------------------
            st.subheader("🧪 Step 3: Generated or Custom Code")
            st.code(generated_code, language="python")

            try:
                local_vars = {"df": df.copy(), "pd": pd}
                exec(generated_code, {}, local_vars)
                ANSWER = local_vars.get("ANSWER", "No variable named ANSWER.")

                # ----------------------------
                # DISPLAY ANSWER
                # ----------------------------
                st.subheader("📈 Step 4: Result")
                st.write(ANSWER)

                # ----------------------------
                # EXPLAIN ANSWER WITH GEMINI
                # ----------------------------
                explain_prompt = f"""
The user asked: {question}  
Here is the result: {ANSWER}

Please explain the answer in natural language. Add helpful insights if applicable.
"""
                with st.spinner("📋 Explaining result..."):
                    explanation = model.generate_content(explain_prompt)
                    st.subheader("🧠 Gemini Explanation")
                    st.markdown(explanation.text)

            except Exception as e:
                st.error(f"❌ Error while executing code: {e}")

    except Exception as e:
        st.error(f"❌ Error reading uploaded files: {e}")

else:
    st.info("📥 Please upload both your **data file** and **data dictionary** to continue.")
