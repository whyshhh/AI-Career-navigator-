import pandas as pd
import random

def analyze_resume(resume_text, job_desc):
    """
    Basic keyword analysis: compare resume vs job description.
    Returns feedback string and keyword density chart.
    """
    resume_words = resume_text.lower().split()
    job_words = job_desc.lower().split()

    matched = [word for word in job_words if word in resume_words]
    feedback = f"Your resume matches {len(set(matched))} out of {len(set(job_words))} job keywords."

    keyword_counts = pd.Series(resume_words).value_counts().head(20)
    return feedback, keyword_counts


def skill_gap_analysis(resume_text, job_desc):
    """
    Identify missing keywords (skill gaps) between resume and job description.
    Returns a list of missing skills/keywords.
    """
    resume_words = set(resume_text.lower().split())
    job_words = set(job_desc.lower().split())

    missing_keywords = job_words - resume_words
    stopwords = {"the", "and", "or", "with", "for", "to", "a", "an", "in", "on", "of"}
    missing_keywords = [kw for kw in missing_keywords if kw not in stopwords and len(kw) > 2]

    return missing_keywords


def generate_mock_questions(missing_keywords, num_questions=5):
    """
    Generate mock interview questions based on missing keywords.
    """
    questions = []
    for kw in random.sample(missing_keywords, min(num_questions, len(missing_keywords))):
        questions.append(f"Can you explain your experience with {kw}?")
        questions.append(f"How have you applied {kw} in past projects?")
    return questions[:num_questions]


def suggest_learning_resources(missing_keywords):
    """
    Map missing keywords to suggested learning resources.
    """
    resources = {}
    for kw in missing_keywords[:10]:  # limit to top 10 gaps
        if "python" in kw:
            resources[kw] = "NPTEL Python Course, LeetCode Python practice"
        elif "java" in kw:
            resources[kw] = "Coursera Java Programming, HackerRank Java challenges"
        elif "ml" in kw or "machine" in kw:
            resources[kw] = "Andrew Ng’s ML course (Coursera), Kaggle tutorials"
        elif "data" in kw or "sql" in kw:
            resources[kw] = "Mode Analytics SQL tutorials, DataCamp Data Science tracks"
        elif "cloud" in kw or "aws" in kw or "azure" in kw:
            resources[kw] = "AWS Academy, Microsoft Learn Azure Fundamentals"
        elif "react" in kw or "frontend" in kw:
            resources[kw] = "FreeCodeCamp React guide, Frontend Mentor projects"
        else:
            resources[kw] = f"Search for {kw} tutorials on Coursera, Udemy, or NPTEL"
    return resources