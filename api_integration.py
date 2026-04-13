import os
from dotenv import load_dotenv
import google.generativeai as genai   # correct package
from groq import Groq

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def recruiter_feedback(resume_text, job_desc, persona="General Recruiter"):
    """
    Generate recruiter-style feedback using Gemini.
    If Gemini quota is exceeded or fails, fallback to Groq.
    Persona allows tailoring feedback style (Startup HR, Corporate Recruiter, Tech Lead).
    Returns: (feedback_text, rate_limited_flag)
    """
    try:
        # Use a valid Gemini model from list_models()
        model = genai.GenerativeModel("models/gemini-2.5-pro")

        prompt = f"""
        Act like a {persona}.
        Compare this resume:
        {resume_text}

        Against this job description:
        {job_desc}

        Provide strengths, weaknesses, missing keywords, and overall recruiter-style feedback.
        """
        response = model.generate_content(prompt)
        return response.text, False

    except Exception as e:
        # Fallback to Groq if Gemini fails
        try:
            groq_prompt = f"""
            Act like a {persona}.
            Compare this resume:
            {resume_text}

            Against this job description:
            {job_desc}

            Provide strengths, weaknesses, missing keywords, and overall recruiter-style feedback.
            """
            groq_response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # supported Groq model
                messages=[{"role": "user", "content": groq_prompt}]
            )
            return groq_response.choices[0].message.content, True
        except Exception as groq_error:
            return f"Both Gemini and Groq failed. Error: {str(groq_error)}", True