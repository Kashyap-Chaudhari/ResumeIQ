<div align="center">
  <h1>🚀 ResumeIQ</h1>
  <p><strong>Your Personal AI Resume Analyzer & Placement Career Coach</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://www.djangoproject.com/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

<br />

**ResumeIQ** is a production-ready, full-stack SaaS platform designed to transform job seekers into top-tier candidates. It leverages AI-driven resume parsing, ATS scoring, Job Description matching, and skill gap detection, while providing AI interview coaching and personalized career roadmaps.

---

## ✨ Core Features

- **🛡️ Secure User Authentication & Profiles:** Robust Django session auth for Registration, Login, and Profile Management (target roles, experience, theme preferences, and optional Google Gemini API Key override).
- **📄 AI Resume Parsing & ATS Scoring:** Extracts data from PDFs via `pdfplumber` (fallback to PyPDF2) and computes a comprehensive 0-100 ATS Score across Keywords, Metrics, Structure, Action Verbs, and Completeness. Extracts over 250 tech skills.
- **🎯 TF-IDF & Cosine Similarity Job Matcher:** Matches uploaded resumes against target Job Descriptions using `scikit-learn` to identify missing skills, providing actionable optimization steps.
- **✨ AI Resume Bullet Rewriter:** Instantly transforms weak, generic bullet points into STAR-method power bullets with quantifiable impact metrics.
- **🎙️ AI Interview Coach:** Generates role-tailored technical, system design, and behavioral questions. Evaluates responses live with constructive feedback and scoring.
- **📊 Readiness Score & Radar Charts:** Visualizes candidate readiness across 5 dimensions using stunning **Chart.js** interactive radar charts.
- **🗺️ Personalized Career Roadmap:** Generates a 4-phase learning path timeline tailored to missing skills with clear action items.
- **📝 Job Application Kanban Tracker:** Track your pipeline across 5 stages: Saved, Applied, Interviewing, Offer, and Rejected.
- **🔄 Resume Versioning & Diff:** Compare ATS scores and skill changes between resume versions over time.
- **📚 Free Learning Resources Hub:** A curated library of top free courses, documentation, and tutorials mapped to your missing skills.

---

## 🛠 Tech Stack

**Backend**
- **Framework:** Django 5, Python 3.13
- **Database:** SQLite3 (Local) / PostgreSQL (Production)
- **AI & ML:** Google Gemini Free API (`google-generativeai`), `scikit-learn` (TF-IDF + Cosine Similarity)
- **NLP & Parsing:** Custom Regex, spaCy, `pdfplumber`, `PyPDF2`

**Frontend**
- **Technologies:** HTML5, CSS3, JavaScript (ES6)
- **Styling:** Bootstrap 5, Custom CSS with Dark & Light modern themes (glassmorphism UI)
- **Visualizations:** Chart.js (Line, Radar, Doughnut)

**Deployment**
- **Hosting:** Render / Heroku
- **Database:** Neon PostgreSQL

---

## 🚀 Quick Start Guide

### 1. Clone & Setup Environment

```bash
git clone https://github.com/your-username/careerpilot-ai.git
cd python_project
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (use `.env.example` as a template):
```env
DEBUG=True
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 5. Setup Database & Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser!

---

## ☁️ Deployment Guide (Render + Neon PostgreSQL)

1. Push your repository to GitHub.
2. Log in to [Render.com](https://render.com).
3. Create a new **Web Service** and connect your GitHub repo.
4. Select environment **Python 3**.
5. Set Build Command:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
6. Set Start Command:
   ```bash
   gunicorn careerpilot.wsgi:application
   ```
7. Add Environment Variables in Render dashboard:
   - `SECRET_KEY`: Random long string
   - `DEBUG`: `False`
   - `GEMINI_API_KEY`: Your Google Gemini API Key

---

## 📄 License

This project is licensed under the **MIT License**. Built to help job seekers accelerate their career growth!
