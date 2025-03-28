import fitz  # PyMuPDF for PDF parsing
import re
import spacy
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

predefined_skills = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#",
    # Web Frameworks & Libraries
    "react", "angular", "vue.js", "node.js", "express", "django", "flask", "spring boot",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "devops",
    # Databases & Data Systems
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "hadoop", "spark", "big data", "mongodb", "sql",
    # AI / Data Science
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "scikit-learn", "data science",
    # Additional Tools
    "git", "linux", "bash", "jenkins", "jira", "agile"
}

# Load BERT model for embeddings
bert_model = SentenceTransformer("all-MiniLM-L6-v2")
# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


# Function to Extract Text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()


def extract_experience_years(resume_text):
    from dateutil import parser
    from datetime import datetime

    doc = nlp(resume_text)
    date_entities = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    job_blocks = []
    total_years = 0

    # Clean and pair dates
    parsed_dates = []
    for date_str in date_entities:
        try:
            parsed_date = parser.parse(date_str, fuzzy=True, default=datetime(1900, 1, 1))
            parsed_dates.append(parsed_date)
        except:
            continue

    # Heuristic: Group by twos (start-end)
    date_pairs = []
    parsed_dates = sorted(parsed_dates)
    for i in range(0, len(parsed_dates) - 1, 2):
        start, end = parsed_dates[i], parsed_dates[i+1]
        if start and end and start < end:
            date_pairs.append((start, end))

    # Calculate total experience from valid ranges
    unique_years = set()
    for start, end in date_pairs:
        for y in range(start.year, end.year + 1):
            unique_years.add(y)

    if unique_years:
        total_years = len(unique_years)

    # Fallback: Use explicit mention of "X years of experience"
    fallback_years = 0
    match = re.search(r"(\d{1,2})\s*(\+?\s*years?|yrs?)\s*(of)?\s*experience", resume_text, re.IGNORECASE)
    if match:
        fallback_years = int(match.group(1))

    # Use the best signal
    final_years = max(total_years, fallback_years)
    return final_years

def extract_resume_info(resume_text):

    resume_info = {"skills": [], "experience": 0, "education": [], "projects": []}
    job_roles = []

    print("\n--- Debugging Resume Extraction ---")
    print(f"Raw Resume Text:\n{resume_text[:500]}...\n")

    # Step 1: Skills Extraction via TF-IDF
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=70,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform([resume_text])
    extracted_terms = vectorizer.get_feature_names_out()

    refined_skills = [
        term for term in extracted_terms
        if term.lower() in predefined_skills
    ]
    resume_info["skills"] = list(set(refined_skills))
    print(f"Extracted Resume Skills (Refined): {resume_info['skills']}")

    # Step 2: Education Extraction
    education_keywords = {"bachelor", "master", "phd", "b.sc", "m.sc", "mba", "degree", "diploma"}
    doc = nlp(resume_text)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "FACILITY"] and "university" in ent.text.lower():
            resume_info["education"].append(ent.text)

    for word in education_keywords:
        if word in resume_text.lower():
            resume_info["education"].append(word.capitalize())

    resume_info["education"] = list(set(resume_info["education"]))
    print(f"Extracted Resume Education: {resume_info['education']}")

    # Final assignment
    resume_info["jobs"] = job_roles
    resume_info["experience"] = extract_experience_years(resume_text)

    print(f"Extracted Resume Experience: {resume_info['experience']} years")
    print(f"Extracted Job Titles: {resume_info['jobs']}")

    return resume_info

def extract_job_info(job_description):
    job_info = {"skills": [], "experience": 0, "education": []}

    print("\n--- Debugging Job Description Extraction ---")
    print(f"Raw Job Description:\n{job_description}\n")

    # TF-IDF for job skill extraction
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=30,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform([job_description])
    important_terms = vectorizer.get_feature_names_out()

    # Match with predefined skills
    job_info["skills"] = [
        skill for skill in important_terms if skill.lower() in predefined_skills
    ]

    print(f"Extracted Job Skills (Top TF-IDF Terms): {job_info['skills']}")

    # Extract years of experience
    exp_match = re.search(r"(\d{1,2})\s*(\+?\s*years?|yrs?)", job_description, re.IGNORECASE)
    if exp_match:
        job_info["experience"] = int(exp_match.group(1))

    # Title-based fallback
    title_experience_mapping = {
        "intern": 0,
        "junior": 1,
        "entry-level": 1,
        "associate": 2,
        "mid-level": 3,
        "software engineer": 3,
        "data scientist": 3,
        "senior": 5,
        "lead": 7,
        "principal": 8,
        "director": 10
    }

    for title, years in title_experience_mapping.items():
        if title in job_description.lower():
            job_info["experience"] = max(job_info["experience"], years)
            break

    print(f"Extracted Job Experience: {job_info['experience']} years")

    # Education extraction
    education_keywords = ["bachelor", "master", "phd", "b.sc", "m.sc", "mba", "degree", "diploma"]
    found_education = []

    lines = job_description.lower().split("\n")
    for line in lines:
        for keyword in education_keywords:
            if keyword in line:
                found_education.append(keyword.capitalize())

    job_info["education"] = list(set(found_education))
    print(f"Extracted Job Education: {job_info['education']}\n")

    return job_info


def rank_resume(resume_info, job_info):
    """
    Ranks a resume based on its match with a job description.
    :param resume_info: Dictionary containing extracted resume details
    :param job_info: Dictionary containing extracted job details
    :return: Resume match score (percentage)
    """

    # Debugging - Print extracted info
    print("\n--- Debug: Resume vs Job Description ---")
    print(f"Resume Skills: {resume_info.get('skills', [])}")
    print(f"Job Skills: {job_info.get('skills', [])}")
    print(f"Resume Experience: {resume_info.get('experience', 0)} years")
    print(f"Job Experience: {job_info.get('experience', 0)} years")
    print(f"Resume Education: {resume_info.get('education', [])}")
    print(f"Job Education: {job_info.get('education', [])}")

    # Normalization Dictionaries
    skill_mapping = {
        "python": ["django", "flask", "fastapi"],
        "javascript": ["react", "angular", "node.js"],
        "machine learning": ["nlp", "deep learning", "tensorflow", "pytorch", "ML"],
        "cloud": ["aws", "azure", "gcp"],
        "database": ["mysql", "postgresql", "mongodb", "sql"]
    }

    education_mapping = {
        "b.sc": "bachelor",
        "bachelor": "bachelor",
        "m.sc": "master",
        "master": "master",
        "phd": "phd",
        "mba": "mba"
    }

    # Normalize Skills
    normalized_resume_skills = set(resume_info.get("skills", []))
    normalized_job_skills = set(job_info.get("skills", []))

    for skill, related_skills in skill_mapping.items():
        if any(rs in normalized_resume_skills for rs in related_skills):
            normalized_resume_skills.add(skill)
        if any(js in normalized_job_skills for js in related_skills):
            normalized_job_skills.add(skill)

    # Skills Match Score
    skill_match_score = len(normalized_resume_skills.intersection(normalized_job_skills)) / len(normalized_job_skills) if normalized_job_skills else 0

    # Normalize Education
    resume_education = resume_info.get("education", [])
    job_education = job_info.get("education", [])  

    normalized_resume_education = set(education_mapping.get(edu.lower(), edu.lower()) for edu in resume_education)
    normalized_job_education = set(education_mapping.get(edu.lower(), edu.lower()) for edu in job_education)

    # Education Match Score
    education_match_score = len(normalized_resume_education.intersection(normalized_job_education)) / len(normalized_job_education) if normalized_job_education else 0

    # Experience Match Score
    resume_experience = resume_info.get("experience", 0)
    job_experience = job_info.get("experience", 0)
    experience_match_score = min(resume_experience / job_experience, 1) if job_experience else 0

    # Final Score Calculation
    scores = [skill_match_score * 100]  # Skills are always considered
    if job_experience > 0:
        scores.append(experience_match_score * 100)
    if job_education:  
        scores.append(education_match_score * 100)

    final_score = sum(scores) / len(scores) if scores else 0  # Prevent division by zero

    print(f"Final Resume Score (After Normalization): {round(final_score, 2)}%\n")

    return round(final_score, 2)

