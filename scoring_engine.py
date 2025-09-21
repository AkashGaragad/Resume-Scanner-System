# scoring_engine.py - The brain of our advanced application
import spacy
from sentence_transformers import SentenceTransformer, util
import re
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# --- Model Loading (Done once at startup) ---
print("Loading AI models for scoring engine...")
try:
    nlp = spacy.load("en_core_web_sm")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("AI models loaded successfully.")
except Exception as e:
    print(f"Error loading AI models: {e}. Please ensure models are downloaded.")
    nlp = None
    embedding_model = None

# --- Scoring Functions ---

def calculate_concept_match_score(jd_text, resume_text):
    """
    Uses TF-IDF to find important concepts in the JD and checks their presence in the resume.
    Returns a score between 0 and 100.
    """
    corpus = [jd_text, resume_text]
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=25)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        jd_scores = tfidf_matrix[0].toarray().flatten()
        
        important_jd_words = [
            feature_names[idx] for idx in np.argsort(jd_scores)[::-1] if jd_scores[idx] > 0.1
        ]
        
        if not important_jd_words:
            return 0
        
        resume_lower = resume_text.lower()
        found_important_words = [word for word in important_jd_words if word in resume_lower]
        
        return (len(found_important_words) / len(important_jd_words)) * 100
    except ValueError:
        # Happens if vocabulary is empty (e.g., all stop words)
        return 0

def extract_experience(resume_text):
    """
    Extracts the highest number of years of experience from resume text using regex.
    """
    patterns = [r'(\d+\.?\d*)\s*\+?\s*years', r'(\d+\.?\d*)\s*\+?\s*yrs']
    found_years = []
    for pattern in patterns:
        matches = re.findall(pattern, resume_text.lower())
        for match in matches:
            try:
                found_years.append(float(match))
            except ValueError:
                continue
    return max(found_years) if found_years else 0

def check_experience_requirement(jd_text, resume_experience_years):
    """
    Checks if the resume's experience meets the requirement from the JD.
    """
    jd_patterns = [r'(\d+\.?\d*)\s*\+?\s*years', r'(\d+\.?\d*)\s*\+?\s*yrs']
    jd_required_years = 0
    for pattern in jd_patterns:
        matches = re.findall(pattern, jd_text.lower())
        for match in matches:
            try:
                jd_required_years = max(jd_required_years, float(match))
            except ValueError:
                continue
    
    if jd_required_years == 0:
        return 100  # No requirement found, so they meet it.
    
    if resume_experience_years >= jd_required_years:
        return 100
    else:
        return max(0, (resume_experience_years / jd_required_years) * 100)

def extract_skills_from_jd(jd_text, skills_library):
    """
    Extracts must-have and good-to-have skills from JD text.
    """
    jd_text_lower = jd_text.lower()
    must_have_skills = set()
    good_to_have_skills = set()
    
    for skill, variations in skills_library.items():
        for variation in variations + [skill.lower()]:
            if variation in jd_text_lower:
                if any(phrase in jd_text_lower for phrase in ["must have", "required", "essential", "proficient in", "need to have"]):
                    must_have_skills.add(skill)
                else:
                    good_to_have_skills.add(skill)
                break
    return must_have_skills, good_to_have_skills

def check_skills_in_resume(resume_text, must_have, good_to_have, skills_library):
    """Checks for the presence of required skills in the resume."""
    resume_text_lower = resume_text.lower()
    found_must = set()
    found_good = set()
    
    for skill_set, found_set in [(must_have, found_must), (good_to_have, found_good)]:
        for skill in skill_set:
            for variation in skills_library[skill] + [skill.lower()]:
                if variation in resume_text_lower:
                    found_set.add(skill)
                    break
    return found_must, found_good

def calculate_skill_score(found_must, found_good, must_have, good_to_have):
    """
    Calculates a weighted skill score.
    70% weight for must-have skills, 30% for good-to-have.
    """
    must_have_ratio = (len(found_must) / len(must_have)) if must_have else 1.0
    good_to_have_ratio = (len(found_good) / len(good_to_have)) if good_to_have else 1.0
    
    score = (must_have_ratio * 0.7) + (good_to_have_ratio * 0.3)
    return score * 100

def calculate_semantic_similarity(jd_text, resume_text):
    """Calculates semantic similarity using sentence embeddings."""
    if not embedding_model:
        return 0.0

    # Encode texts into embeddings
    jd_embedding = embedding_model.encode(jd_text, convert_to_tensor=True)
    resume_embedding = embedding_model.encode(resume_text, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_score = util.pytorch_cos_sim(jd_embedding, resume_embedding).item()
    return max(0, cosine_score * 100) # Ensure score is non-negative

def extract_education(resume_text):
    """Extracts common degree patterns from resume text."""
    education_keywords = ["bachelor", "master", "phd", "b.sc", "m.sc", "b.tech", "m.tech", "b.e.", "m.e.", "degree", "diploma"]
    return [keyword for keyword in education_keywords if keyword in resume_text.lower()]

def check_education_requirement(jd_text, resume_education):
    """Checks if resume education meets JD requirements."""
    jd_lower = jd_text.lower()
    education_terms = ["bachelor", "master", "phd", "diploma", "degree"]
    
    jd_reqs = [term for term in education_terms if term in jd_lower]
    if not jd_reqs:
        return 100  # No specific requirement mentioned.
    
    return 100 if any(req in edu for req in jd_reqs for edu in resume_education) else 0

# --- Main Scoring Orchestrator ---

def calculate_hard_match_score(jd_text, resume_text, skills_library):
    """
    Calculates the overall hard match score based on weighted components.
    """
    # Skills (40%)
    must_have, good_to_have = extract_skills_from_jd(jd_text, skills_library)
    found_must, found_good = check_skills_in_resume(resume_text, must_have, good_to_have, skills_library)
    skill_score = calculate_skill_score(found_must, found_good, must_have, good_to_have)
    
    # Education (20%)
    resume_education = extract_education(resume_text)
    education_score = check_education_requirement(jd_text, resume_education)
    
    # Concepts (30%)
    concept_score = calculate_concept_match_score(jd_text, resume_text)
    
    # Experience (10%)
    resume_exp_years = extract_experience(resume_text)
    exp_score = check_experience_requirement(jd_text, resume_exp_years)
    
    # Apply weights
    hard_score = (skill_score * 0.4) + (education_score * 0.2) + (concept_score * 0.3) + (exp_score * 0.1)
    
    return hard_score, {
        "must_have_skills": must_have, "good_to_have_skills": good_to_have,
        "found_must_have": found_must, "found_good_to_have": found_good,
        "skill_score": skill_score, "education_score": education_score,
        "concept_score": concept_score, "experience_score": exp_score
    }

def generate_gemini_feedback(jd_text, resume_text, missing_skills, final_score, found_skills, api_key):
    """
    Generate personalized feedback for the candidate using Google's Gemini model.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        Analyze the following job description and resume to provide constructive, actionable feedback for the candidate.

        **JOB DESCRIPTION (Excerpt):**
        {jd_text[:500]}...

        **RESUME (Excerpt):**
        {resume_text[:600]}...

        **AUTOMATED ANALYSIS:**
        - Overall Match Score: {final_score:.1f}/100
        - Skills Found: {', '.join(found_skills) if found_skills else 'None of the key skills were explicitly found.'}
        - Key Missing Skills: {', '.join(missing_skills) if missing_skills else 'All key skills appear to be present.'}

        **INSTRUCTIONS:**
        Act as an expert career coach. Provide feedback in the following Markdown format. Be specific, professional, and encouraging.

        ---

        ### 🎯 Executive Summary
        *Provide a 2-3 sentence overview of the candidate's alignment with the role based on the provided data.*

        ### ✅ Strengths
        - **Strength 1:** *Mention a specific strength, such as a key skill they possess or relevant experience.*
        - **Strength 2:** *Mention another positive alignment.*
        - **Strength 3:** *Highlight a third area where they are a good fit.*

        ### 💡 Areas for Improvement
        - **Most Critical Gap:** *Identify the most significant missing skill or experience and suggest a clear, actionable way to address it (e.g., a specific online course, a type of project to build).*
        - **Resume Tailoring:** *Suggest a specific change to their resume to better highlight their fit for this particular job (e.g., "Consider adding a project that demonstrates your experience with 'Python' and 'data analysis' to the top of your experience section.").*
        - **Interview Preparation:** *Advise them on what to emphasize during an interview to overcome any perceived gaps.*
        """

        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") and response.text else "⚠️ AI feedback could not be generated."
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return f"⚠️ Could not generate AI feedback due to an error: {str(e)}"
