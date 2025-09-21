# Automated Resume Relevance Check System

**Hosted URL:**  
[👉 Live Demo](https://resume-scanner-system-and-analyzer-fk8bgvj6pbodow8evkopx4.streamlit.app/)

---

## 📌 Problem Statement

At **Innomatics Research Labs**, resume evaluation is currently **manual, inconsistent, and time-consuming**.  
Every week, the placement team across **Hyderabad, Bangalore, Pune, and Delhi NCR** receives **18–20 job requirements**, with each posting attracting **thousands of applications**.

Challenges with the manual process:
- ❌ Delays in shortlisting candidates.  
- ❌ Inconsistent judgments, as evaluators may interpret requirements differently.  
- ❌ High workload for placement staff, limiting focus on student interview prep.  
- ❌ Hiring companies expect **fast and high-quality** shortlists.  

Hence, there is a pressing need for an **automated system** that is **scalable, consistent, and provides actionable feedback** to students.

---

## 🎯 Objective

The **Automated Resume Relevance Check System** aims to:

- Automate resume evaluation against job requirements at scale.  
- Generate a **Relevance Score (0–100)** for each resume.  
- Highlight **missing skills, certifications, or projects**.  
- Provide a **fit verdict**: High / Medium / Low suitability.  
- Offer **personalized improvement feedback** to students.  
- Store evaluations in a **web-based dashboard** accessible to the placement team.  
- Handle **thousands of resumes weekly** with consistency and robustness.  

---

## 🚀 Proposed Solution

We propose building an **AI-powered resume evaluation engine** that combines **rule-based checks** with **LLM-powered semantic understanding**.

### Key Steps
1. **Job Requirement Upload** – Placement team uploads job descriptions (JD).  
2. **Resume Upload** – Students upload resumes (PDF/DOCX).  
3. **Resume Parsing** – Extract raw text, normalize sections.  
4. **JD Parsing** – Extract job role, must-have and nice-to-have skills.  
5. **Relevance Analysis** –  
   - Hard Match: keyword & skill check (exact + fuzzy).  
   - Semantic Match: embeddings + LLM reasoning.  
   - Scoring: weighted formula for final score.  
6. **Output Generation** –  
   - Relevance Score (0–100).  
   - Missing skills/projects.  
   - Verdict: High / Medium / Low.  
   - Suggestions for improvement.  
7. **Storage & Dashboard** – Results stored in a database, accessible via a searchable web app.  

---

## 🛠 Features

- 📄 Resume text extraction (PDF, DOCX).  
- 🤖 AI-powered semantic comparison with job descriptions.  
- 📊 Automatic scoring (0–100) based on hard + soft matching.  
- 🔍 Highlight missing skills, certifications, and projects.  
- 📝 Personalized improvement feedback for students.  
- 📂 Placement team dashboard to manage resumes & JDs.  
- ⚡ Scalable – handles **thousands of resumes weekly**.  

---

## 🏗 Tech Stack

### Core Resume Parsing & AI
- **Python** – backend language  
- **PyMuPDF / pdfplumber** – PDF parsing  
- **python-docx / docx2txt** – DOCX parsing  
- **spaCy / NLTK** – entity extraction & text normalization  
- **LangChain / LangGraph / LangSmith** – LLM orchestration, observability  
- **Vector Stores**: Chroma / FAISS / Pinecone – embeddings & semantic search  
- **LLMs**: OpenAI GPT / Gemini / Claude / HuggingFace – semantic matching & feedback  
- **Keyword Matching**: TF-IDF, BM25, fuzzy search  
- **Scoring**: Hard + Soft match weighted formula  

### Web Application
- **Flask / FastAPI** – APIs for resume & JD processing  
- **Streamlit (MVP)** – front-end dashboard  
- **SQLite / PostgreSQL** – results storage & metadata  

---

## ⚙️ Installation Steps

To set up locally:

```bash
# 1. Clone the repository
git clone <your_repo_url>
cd resume-scanner-system

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
