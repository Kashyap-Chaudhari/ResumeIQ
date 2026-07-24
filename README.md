<div align="center">
  <h1>🚀 ResumeIQ</h1>
  <p><strong>Next-Gen AI Resume Analyzer, Job Matcher & Placement Career Coach</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
  [![Django](https://img.shields.io/badge/Django-5.0-092E20.svg)](https://www.djangoproject.com/)
  [![Google Gemini](https://img.shields.io/badge/AI-Google_Gemini_API-8E44AD.svg)](https://ai.google.dev/)
  [![Database](https://img.shields.io/badge/Database-Neon_PostgreSQL-00E599.svg)](https://neon.tech/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

<br />

**ResumeIQ** is a production-ready, full-stack AI SaaS platform designed to empower job seekers, students, and professionals to land their dream software engineering and tech roles. It seamlessly combines AI resume parsing, ATS scoring, TF-IDF job description matching, AI interview coaching, interactive readiness radar charts, and personalized learning roadmaps into a single premium SaaS interface.

---

## 🌟 What's New in Latest Update

- **🔐 Premium Glassmorphism Auth Suite (`#0B1020` Theme):**
  - Completely redesigned **Login** & **Registration (Create Account)** pages featuring dark SaaS aesthetics, ambient animated glowing orbs, floating particle background canvas, and glowing brand logo boxes.
  - **Live Password Validation Checklist:** Interactive real-time verification of password criteria (8+ characters, uppercase letter, number, and special character).
  - **⚡ 1-Click Demo Access Card:** Built-in demo credentials card with auto-fill & copy clipboard capabilities (`demo_student` / `Demo@123`).
- **🎨 Refined Topbar & Navigation UI:**
  - Expanded user profile badge with rounded squircle avatar, bold typography, and smooth dark/light theme switching.
- **🗺️ Enhanced Learning Roadmaps:**
  - Streamlined step-by-step career path visualization and session history management.

---

## ✨ Key Features

- **📄 AI Resume Parsing & ATS Scoring:** Extracts text and structure from uploaded PDF resumes using `pdfplumber` (with `PyPDF2` fallback) and computes a comprehensive 0–100 ATS Score across Keywords, Quantifiable Metrics, Structure, Action Verbs, and Completeness. Automatically detects over 250+ tech skills.
- **🎯 TF-IDF & Cosine Similarity Job Matcher:** Leverages `scikit-learn` to calculate exact match percentages between candidate resumes and target Job Descriptions, highlighting critical missing keywords and skills.
- **✨ AI Resume Bullet Rewriter:** Instantly transforms generic or weak bullet points into STAR-formatted (Situation, Task, Action, Result) power statements backed by metrics.
- **🎙️ AI Interview Coach:** Generates role-tailored technical, system design, and behavioral questions. Offers real-time evaluation and feedback on candidate answers.
- **📊 Placement Readiness Radar Chart:** Visualizes overall job readiness across 5 dimensions using interactive **Chart.js** radar charts.
- **🗺️ Personalized Career Roadmap:** Generates structured, step-by-step learning milestones tailored to candidate skill gaps and target roles.
- **📋 Job Application Kanban Tracker:** Helps candidates manage job applications across 5 pipeline stages (Saved, Applied, Interviewing, Offer, Rejected).
- **📚 Free Learning Resources Hub:** Curated library of top documentation, tutorials, and courses mapped to candidate skill gaps.

---

## 🛠 Tech Stack

### **Backend**
- **Framework:** Django 5, Python 3.13
- **Database:** SQLite3 (Local) / Neon PostgreSQL (Production)
- **AI & ML:** Google Gemini AI API (`google-generativeai`), `scikit-learn` (TF-IDF & Cosine Similarity)
- **NLP & PDF Processing:** Custom Regex, `pdfplumber`, `PyPDF2`

### **Frontend**
- **Core Technologies:** HTML5, JavaScript (ES6), CSS3 (Custom Glassmorphism SaaS System)
- **Styling:** Bootstrap 5.3, Bootstrap Icons, Google Fonts (Plus Jakarta Sans & Inter)
- **Data Visualization:** Chart.js (Interactive Radar & Progress Charts)

### **Deployment & Cloud Infrastructure**
- **Hosting:** Vercel / Render
- **Production Database:** Neon PostgreSQL
- **Static Assets:** Whitenoise / Django Static

---

## 🚀 Quick Start Guide

### 1. Clone Repository

```bash
git clone https://github.com/Kashyap-Chaudhari/ResumeIQ.git
cd ResumeIQ
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory (refer to `.env.example`):

```env
DEBUG=True
SECRET_KEY=your_django_secret_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 5. Run Database Migrations & Create Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser!

---

## ⚡ Demo Access

For quick testing without creating a new account:
- **Username:** `demo_student`
- **Password:** `Demo@123`

*(You can also click the **"Copy Credentials"** button on the Login page to automatically fill in these credentials.)*

---

## ☁️ Production Deployment

### **Deploying to Vercel / Render + Neon DB**

1. Push your latest changes to GitHub.
2. Link repository to Vercel / Render dashboard.
3. Configure the environment variables in your deployment dashboard:
   - `SECRET_KEY`
   - `DEBUG` = `False`
   - `DATABASE_URL` = *(Neon PostgreSQL Connection String)*
   - `GEMINI_API_KEY` = *(Google Gemini API Key)*
4. Build command:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

---

## 📄 License

This project is licensed under the **MIT License**. Built with ❤️ to help software engineers and candidates land their dream careers!
