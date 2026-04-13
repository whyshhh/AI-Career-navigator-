import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF

from navigator import analyze_resume, skill_gap_analysis, generate_mock_questions, suggest_learning_resources
from api_integration import recruiter_feedback
from utils import extract_text_from_file

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="AI Career Navigator", layout="wide")
st.title("🚀 AI Career Navigator")

# -------------------------------
# Recruiter Persona Selector
# -------------------------------
persona = st.selectbox("Choose recruiter persona", ["Startup HR", "Corporate Recruiter", "Tech Lead"])

# -------------------------------
# Initialize Session State
# -------------------------------
for key, default in {
    "resume_text": "",
    "job_desc": "",
    "feedback": "",
    "keyword_chart": None,
    "ai_feedback": "",
    "missing_keywords": [],
    "mock_questions": [],
    "resources": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Resume Upload",
    "📊 Keyword Analysis",
    "🤖 Recruiter Feedback",
    "🎤 Career Guidance"
])

# -------------------------------
# Tab 1: Resume Upload
# -------------------------------
with tab1:
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    resume_text = ""
    if resume_file is not None:
        resume_text = extract_text_from_file(resume_file)

    if not resume_text:
        resume_text = st.text_area("Or paste your resume text", height=200)

    job_desc = st.text_area("Paste Job Description", height=200)

    if st.button("Analyze"):
        if resume_text and job_desc:
            st.session_state.resume_text = resume_text
            st.session_state.job_desc = job_desc
            st.session_state.feedback, st.session_state.keyword_chart = analyze_resume(resume_text, job_desc)
            st.session_state.ai_feedback, st.session_state.rate_limited = recruiter_feedback(
                resume_text, job_desc, persona
            )
            st.session_state.missing_keywords = skill_gap_analysis(resume_text, job_desc)
            st.session_state.mock_questions = generate_mock_questions(st.session_state.missing_keywords)
            st.session_state.resources = suggest_learning_resources(st.session_state.missing_keywords)
        else:
            st.warning("Please provide both resume and job description.")

# -------------------------------
# Tab 2: Keyword Analysis
# -------------------------------
# -------------------------------
# Tab 2: Keyword Analysis
# -------------------------------
with tab2:
    if st.session_state.feedback:
        st.subheader("Keyword Match Feedback")
        st.write(st.session_state.feedback)

    if st.session_state.keyword_chart is not None and not st.session_state.keyword_chart.empty:
        st.subheader("Keyword Analysis")

        col1, col2 = st.columns(2)

        # Horizontal Bar Chart
        with col1:
            fig, ax = plt.subplots()
            ax.barh(st.session_state.keyword_chart.index,
                    st.session_state.keyword_chart.values,
                    color="skyblue")
            ax.set_title("Keyword Frequency")
            ax.set_xlabel("Count")
            st.pyplot(fig)

        # Pie Chart
        with col2:
            fig, ax = plt.subplots()
            ax.pie(st.session_state.keyword_chart.values,
                   labels=st.session_state.keyword_chart.index,
                   autopct='%1.1f%%',
                   startangle=90,
                   colors=plt.cm.Paired.colors)
            ax.set_title("Keyword Distribution")
            st.pyplot(fig)

# -------------------------------
# Tab 3: Recruiter Feedback
# -------------------------------
with tab3:
    if st.session_state.ai_feedback:
        st.subheader(f"AI Recruiter Feedback ({persona})")
        st.write(st.session_state.ai_feedback)

        # PDF Export with Unicode-safe handling
        def sanitize_text(text):
            replacements = {
                "“": '"', "”": '"',
                "‘": "'", "’": "'",
                "✅": "[OK]", "⚠️": "[Warning]",
                "•": "-", "→": "->"
            }
            for bad, good in replacements.items():
                text = text.replace(bad, good)
            return text

        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()

            # Try to use a Unicode font if available
            try:
                pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=12)
            except:
                pdf.set_font("Arial", size=12)

            safe_feedback = sanitize_text(st.session_state.ai_feedback)

            # Title
            pdf.set_font_size(14)
            pdf.cell(200, 10, "AI Career Navigator Report", ln=True, align="C")
            pdf.ln(10)

            # Recruiter Feedback Section
            pdf.set_font_size(12)
            pdf.cell(200, 10, "Recruiter Feedback", ln=True)
            pdf.multi_cell(0, 10, safe_feedback)
            pdf.ln(5)

            # Strengths & Weaknesses headings (if feedback contains them)
            pdf.set_font_size(12)
            pdf.cell(200, 10, "Strengths", ln=True)
            pdf.multi_cell(0, 10, "Highlight your enthusiasm, relevant experiences, and communication skills.")
            pdf.ln(5)

            pdf.cell(200, 10, "Weaknesses", ln=True)
            pdf.multi_cell(0, 10, "Add depth in technical skills, improve formatting consistency, and use action verbs.")
            pdf.ln(10)

            # Keyword Density Section
            pdf.set_font_size(12)
            pdf.cell(200, 10, "Keyword Density", ln=True)

            if st.session_state.keyword_chart is not None and not st.session_state.keyword_chart.empty:
                pdf.set_font_size(11)
                pdf.cell(100, 10, "Keyword", border=1)
                pdf.cell(50, 10, "Frequency", border=1, ln=True)
                for k, v in st.session_state.keyword_chart.items():
                    pdf.cell(100, 10, sanitize_text(str(k)), border=1)
                    pdf.cell(50, 10, str(v), border=1, ln=True)

            # Return as bytes
            pdf_bytes = pdf.output(dest="S")
            return bytes(pdf_bytes)

        pdf_bytes = generate_pdf()

        st.download_button(
            label="📥 Download Report as PDF",
            data=pdf_bytes,
            file_name="resume_report.pdf",
            mime="application/pdf"
        )

# -------------------------------
# Tab 4: Career Guidance
# -------------------------------
with tab4:
    if st.session_state.missing_keywords:
        st.subheader("Career Guidance (Skill Gap Analysis)")
        st.write("📌 Missing Keywords/Skills from your resume:")
        st.write(", ".join(st.session_state.missing_keywords[:30]))

        st.subheader("🎤 Mock Interview Questions")
        for q in st.session_state.mock_questions:
            st.write(f"- {q}")

        st.subheader("📚 Suggested Learning Resources")
        for kw, resource in st.session_state.resources.items():
            st.write(f"- **{kw}** → {resource}")

        st.info("Tip: Use these resources to close skill gaps and improve your recruiter appeal.")