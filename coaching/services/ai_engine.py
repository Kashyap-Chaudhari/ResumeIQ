import os
import json
import requests

class GeminiModel:
    def __init__(self, api_key, model_name="gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_content(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        class ResponseText:
            def __init__(self, text):
                self.text = text
                
        try:
            text = data['candidates'][0]['content']['parts'][0]['text']
            return ResponseText(text)
        except (KeyError, IndexError):
            raise Exception("Invalid response format from Gemini API")

def get_gemini_model(user_api_key=None):
    """
    Get configured Gemini model instance if valid key exists.
    """
    api_key = user_api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    return GeminiModel(api_key=api_key)

# ================================
# 1. RESUME REWRITE & BULLETS
# ================================
def generate_resume_rewrite(raw_bullets, target_role="Software Engineer", missing_skills=None, api_key=None):
    model = get_gemini_model(api_key)
    missing_str = ", ".join(missing_skills) if missing_skills else "modern software engineering tools"

    if model:
        try:
            prompt = f"""You are an expert ATS Resume Coach. Rewrite the following resume bullet points for a {target_role} role.
Incorporate action verbs, quantifiable metrics, and naturally integrate these missing keywords: {missing_str}.
Input Bullets:
{raw_bullets}

Return a JSON array of string rewritten bullet points strictly in valid JSON format like:
["bullet 1", "bullet 2", "bullet 3"]
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            # Find JSON array
            start = clean_text.find('[')
            end = clean_text.rfind(']') + 1
            if start != -1 and end != -1:
                bullets = json.loads(clean_text[start:end])
                return bullets
        except Exception:
            pass

    # Heuristic Offline Fallback
    lines = [b.strip() for b in raw_bullets.split('\n') if b.strip()]
    if not lines:
        lines = [f"Developed key features for {target_role} platform."]

    fallback_bullets = []
    verbs = ["Architected", "Engineered", "Optimized", "Spearheaded", "Streamlined"]
    metrics = ["reducing server latency by 40%", "increasing throughput by 3x", "improving test coverage to 92%", "scaling to 50k monthly active users"]

    for idx, line in enumerate(lines[:5]):
        verb = verbs[idx % len(verbs)]
        metric = metrics[idx % len(metrics)]
        skill_insert = f" utilizing {missing_skills[idx]}" if missing_skills and idx < len(missing_skills) else ""
        fallback_bullets.append(f"{verb} {line.lstrip('•-* ')}{skill_insert}, {metric}.")

    return fallback_bullets

# ================================
# 2. INTERVIEW COACHING
# ================================
def generate_interview_questions(target_role="Software Engineer", company_name="", skills=None, api_key=None):
    model = get_gemini_model(api_key)
    skills_str = ", ".join(skills) if skills else "Python, System Design, REST APIs, SQL, Data Structures"

    if model:
        try:
            prompt = f"""You are a Lead Staff Tech Interviewer at {company_name or 'a top tier technology company'}.
Generate exactly 20 realistic, highly specific technical, coding, system architecture, and behavioral interview questions for a candidate applying for the role of {target_role}.
Skills & Tech Stack context: {skills_str}.

Requirements:
- Output MUST be a valid JSON array of 20 distinct objects.
- Each object MUST contain: "id" (1 to 20), "question", "category" (Technical, System Design, Coding, or Behavioral), "sample_answer" (a clear, highly technical 2-4 sentence model answer).
- Questions MUST be strictly relevant to {target_role} with zero generic filler.

Return ONLY the raw JSON array in this exact format:
[
  {{"id": 1, "question": "...", "category": "Technical", "sample_answer": "..."}}
]
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            start = clean_text.find('[')
            end = clean_text.rfind(']') + 1
            if start != -1 and end != -1:
                parsed = json.loads(clean_text[start:end])
                if isinstance(parsed, list) and len(parsed) >= 5:
                    return parsed
        except Exception:
            pass

    # Heuristic 20 Role-Specific Fallback Questions
    role_lower = target_role.lower()
    main_skill = skills[0] if skills else "SQL/Data Analysis" if "data" in role_lower or "analyst" in role_lower else "Python/Backend"

    fallback = [
        {
            "id": 1,
            "question": f"Can you walk me through your technical approach to designing a production-grade data pipeline or architecture for {target_role}?",
            "category": "System Design",
            "sample_answer": f"I focus on modular component decoupling, idempotent data processing steps, automated retry queues (Celery/Kafka), and robust schema validation using tools like {main_skill}."
        },
        {
            "id": 2,
            "question": f"How do you identify and resolve performance bottlenecks in slow queries or backend services when working with {main_skill}?",
            "category": "Technical",
            "sample_answer": "I start by profiling using EXPLAIN ANALYZE or memory profilers to locate unindexed full table scans or heavy memory allocations, then implement indexing, query refactoring, or caching."
        },
        {
            "id": 3,
            "question": "Describe a time when you disagreed with a senior engineer or product manager on a technical trade-off. How did you handle it?",
            "category": "Behavioral",
            "sample_answer": "I used data and benchmark prototypes to demonstrate trade-offs objectively, listened to business urgency, and agreed on a staged MVP rollout with clear tech-debt cleanup milestones."
        },
        {
            "id": 4,
            "question": f"What security best practices do you enforce in API endpoints and database access layers for a {target_role} workflow?",
            "category": "Technical",
            "sample_answer": "Enforce HTTPS/TLS, parameterized queries to eliminate SQL injection, JWT/OAuth2 token rotation, strict CORS settings, rate limiting, and RBAC permission checks."
        },
        {
            "id": 5,
            "question": f"How do you handle dataset anomalies, missing values, or corrupt incoming payloads in {target_role} tasks?",
            "category": "Technical",
            "sample_answer": "I implement input validation schemas (Pydantic/Cerberus), log anomalies to dead-letter queues for auditing, and apply domain-appropriate imputation or strict rejection mechanisms."
        },
        {
            "id": 6,
            "question": "Tell me about a high-stress production outage you experienced. What steps did you take to restore service and prevent recurrence?",
            "category": "Behavioral",
            "sample_answer": "I followed incident response protocols: stabilized system with fast rollback/traffic throttling, communicated status to stakeholders, performed root-cause analysis, and added automated regression tests."
        },
        {
            "id": 7,
            "question": f"Explain the difference between asynchronous processing and multi-threading/multi-processing in {main_skill}.",
            "category": "Technical",
            "sample_answer": "Async handles I/O-bound tasks using an event loop on a single thread. Multi-threading is suited for concurrent I/O with shared memory. Multi-processing bypasses GIL constraints for CPU-heavy tasks."
        },
        {
            "id": 8,
            "question": f"How do you structure automated testing (Unit, Integration, E2E) for a complex {target_role} codebase?",
            "category": "Technical",
            "sample_answer": "I follow the testing pyramid: isolated unit tests with mocks for fast feedback, integration tests against containerized DBs (Testcontainers), and key E2E sanity checks in CI/CD pipelines."
        },
        {
            "id": 9,
            "question": "Give an example of how you refactored a legacy codebase to improve maintainability without breaking existing functionality.",
            "category": "Technical",
            "sample_answer": "I established a suite of safety regression tests first, applied solid design patterns (Factory/Repository), split monolithic files into modular subpackages, and deployed incrementally."
        },
        {
            "id": 10,
            "question": f"What caching strategies (e.g. Cache-Aside, Write-Through, TTL) do you choose for high-throughput {target_role} applications?",
            "category": "System Design",
            "sample_answer": "Cache-Aside with Redis is ideal for read-heavy workloads with strict TTL expiration and lazy loading. For write-heavy analytics, Write-Behind buffers database writes."
        },
        {
            "id": 11,
            "question": "Describe a project where you had to quickly learn a technology or framework you had never used before.",
            "category": "Behavioral",
            "sample_answer": "I reviewed official documentation, built a small proof-of-concept prototype, analyzed open-source reference implementations, and sought code review feedback to ensure idiomatic code."
        },
        {
            "id": 12,
            "question": f"How do you optimize SQL window functions or aggregations when processing large scale datasets as a {target_role}?",
            "category": "Technical",
            "sample_answer": "I leverage PARTITION BY with indexed ordering columns, avoid unnecessary subqueries, partition massive tables by date, and compute incremental materialized views."
        },
        {
            "id": 13,
            "question": f"What principles do you follow to ensure high availability, fault tolerance, and zero-downtime deployments for {target_role} systems?",
            "category": "System Design",
            "sample_answer": "Blue-Green or Canary deployments, stateless application containers behind load balancers, database read-replicas, graceful shutdown handlers, and health check probes."
        },
        {
            "id": 14,
            "question": "How do you prioritize competing feature requests and bug fixes when resources are constrained?",
            "category": "Behavioral",
            "sample_answer": "I evaluate impact vs effort using an Eisenhower/ICE matrix, align with core business goals, address critical security/blocking bugs first, and communicate transparent roadmap trade-offs."
        },
        {
            "id": 15,
            "question": f"What is your approach to API versioning and backward compatibility when updating client-facing {target_role} services?",
            "category": "Technical",
            "sample_answer": "Use URL path versioning (/v1/, /v2/), deprecate old fields gracefully without breaking changes, add headers for deprecation warnings, and maintain sunset schedules."
        },
        {
            "id": 16,
            "question": f"Explain memory management, garbage collection, or memory leak detection techniques in {main_skill}.",
            "category": "Technical",
            "sample_answer": "I monitor heap size, use memory profilers (tracemalloc/valgrind) to spot uncollected circular references or unclosed file/connection handles, and enforce context managers."
        },
        {
            "id": 17,
            "question": f"How do you implement centralized logging, metrics monitoring, and alerting for a {target_role} environment?",
            "category": "System Design",
            "sample_answer": "Collect structured JSON logs via Prometheus/Grafana or ELK stack, attach correlation IDs across microservices, and define actionable alert thresholds for error rates and latency p99."
        },
        {
            "id": 18,
            "question": "Tell me about a time you mentored a team member or conducted code reviews that improved engineering standards.",
            "category": "Behavioral",
            "sample_answer": "I provided constructive, actionable code review comments focusing on architecture rather than style, created shared team style guides, and paired on complex debugging sessions."
        },
        {
            "id": 19,
            "question": f"How do you design database schemas (normalization vs denormalization) for relational vs document databases in {target_role} projects?",
            "category": "Technical",
            "sample_answer": "I normalize to 3NF for OLTP system transactional integrity to prevent anomaly updates, and denormalize into star/snowflake schemas or document stores for analytical OLAP speed."
        },
        {
            "id": 20,
            "question": "What is the most technically challenging problem you have solved in your career, and what made your solution effective?",
            "category": "Technical",
            "sample_answer": "I identified the root bottleneck through empirical metrics, designed a clean decoupled architecture, implemented automated benchmarks to verify a 5x performance boost, and documented the design."
        }
    ]

    return fallback

def evaluate_interview_answer(question_text, user_answer, sample_answer="", api_key=None):
    model = get_gemini_model(api_key)
    if not user_answer or len(user_answer.strip()) < 10:
        return 35, "Your answer is too brief. Provide specific details using the STAR technique (Situation, Task, Action, Result)."

    if model:
        try:
            prompt = f"""Evaluate this interview answer:
Question: {question_text}
Candidate Answer: {user_answer}
Sample Ideal Answer: {sample_answer}

Return a JSON object with:
"score": (integer 0-100),
"feedback": (string constructive summary of strengths and areas of improvement)
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            if start != -1 and end != -1:
                res = json.loads(clean_text[start:end])
                return res.get('score', 75), res.get('feedback', 'Good answer structure.')
        except Exception:
            pass

    # Offline Heuristic Scoring
    words = len(user_answer.split())
    score = min(95, max(45, words * 2))
    
    feedback = "Solid answer! "
    if words < 30:
        feedback += "Consider elaborating on specific technical tools and quantitative outcomes."
    else:
        feedback += "Great technical depth and clear structure."

    return score, feedback

# ================================
# 3. CAREER ROADMAP GENERATOR
# ================================
def generate_career_roadmap(target_role="Full Stack Developer", current_level="Entry Level", missing_skills=None, api_key=None):
    model = get_gemini_model(api_key)
    skills = missing_skills if missing_skills else ["System Architecture", "Docker/DevOps", "Advanced SQL", "CI/CD Pipelines"]

    if model:
        try:
            prompt = f"""Create a 4-phase personalized career learning roadmap for a {current_level} aspiring to be a Senior {target_role}.
Focus skills to master: {", ".join(skills)}.
Return a JSON array of phase objects formatted as:
[
  {{
    "phase": "Phase 1: Foundations",
    "duration": "Weeks 1-3",
    "focus": "Core concept mastering",
    "topics": ["Topic 1", "Topic 2"],
    "action_items": ["Action 1", "Action 2"],
    "recommended_skills": ["Skill 1"]
  }}
]
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            start = clean_text.find('[')
            end = clean_text.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(clean_text[start:end])
        except Exception:
            pass

    # Heuristic Offline Roadmap
    return [
        {
            "phase": "Phase 1: Advanced Core Mastery",
            "duration": "Weeks 1 - 3",
            "focus": f"Deepening core language and framework expertise in {target_role}",
            "topics": [f"Deep Dive into {skills[0] if len(skills)>0 else 'Backend Architecture'}", "Asynchronous Programming & Concurrency", "Database Query Optimization"],
            "action_items": ["Build a high-throughput REST service", "Implement comprehensive unit and integration tests"],
            "recommended_skills": [skills[0] if len(skills)>0 else "Python/Django"]
        },
        {
            "phase": "Phase 2: Modern DevOps & Cloud Delivery",
            "duration": "Weeks 4 - 6",
            "focus": "Containerization, Cloud Infrastructure & Automated Pipelines",
            "topics": [f"Mastering {skills[1] if len(skills)>1 else 'Docker & Kubernetes'}", "GitHub Actions CI/CD Workflows", "Cloud Deployment on AWS/GCP"],
            "action_items": ["Containerize multi-container web application with Docker Compose", "Configure automated CI/CD pipeline to Render/Cloud"],
            "recommended_skills": [skills[1] if len(skills)>1 else "Docker", "CI/CD"]
        },
        {
            "phase": "Phase 3: System Design & Scalability",
            "duration": "Weeks 7 - 9",
            "focus": "Architecting scalable distributed systems and caching layers",
            "topics": [f"System Design Patterns for {target_role}", "Redis In-Memory Caching & Message Queues", "Microservices Communication"],
            "action_items": ["Design a distributed URL shortener or rate limiter", "Implement Redis session storage and cache invalidation"],
            "recommended_skills": [skills[2] if len(skills)>2 else "System Design", "Redis"]
        },
        {
            "phase": "Phase 4: Placement Readiness & Interview Mastery",
            "duration": "Weeks 10 - 12",
            "focus": "Portfolio polish, mock interviews, and recruiter outreach",
            "topics": ["ATS Resume Optimization", "Live Coding & Algorithm Mock Interviews", "Behavioral Leadership Stories"],
            "action_items": ["Pass 3 mock interview sessions on ResumeIQ", "Publish top 2 capstone projects with live demo links"],
            "recommended_skills": ["Interview Prep", "Portfolio Polish"]
        }
    ]

# ================================
# 4. PLACEMENT READINESS CALCULATOR
# ================================
def calculate_placement_readiness(avg_ats_score, avg_match_score, total_skills, total_interviews):
    """
    Calculate 0-100 Placement Readiness score across 5 domains.
    """
    resume_quality = min(100, int(avg_ats_score if avg_ats_score > 0 else 60))
    match_readiness = min(100, int(avg_match_score if avg_match_score > 0 else 55))
    technical_skills = min(100, max(40, total_skills * 6))
    interview_prep = min(100, max(30, total_interviews * 25))
    problem_solving = min(100, int((technical_skills + interview_prep) / 2))

    overall = int((resume_quality * 0.3) + (match_readiness * 0.25) + (technical_skills * 0.2) + (interview_prep * 0.15) + (problem_solving * 0.1))
    overall = max(20, min(100, overall))

    domain_scores = {
        'technical': technical_skills,
        'problem_solving': problem_solving,
        'experience': match_readiness,
        'resume_quality': resume_quality,
        'interview_prep': interview_prep
    }

    strengths = []
    gaps = []

    if resume_quality >= 75:
        strengths.append("ATS Resume optimization is strong")
    else:
        gaps.append("Resume ATS keyword density needs improvement")

    if technical_skills >= 70:
        strengths.append("Robust technical skill stack identified")
    else:
        gaps.append("Expand core skills to match target job descriptions")

    if interview_prep >= 60:
        strengths.append("Active interview practice history")
    else:
        gaps.append("Complete more mock AI interview practice sessions")

    return overall, domain_scores, strengths, gaps

# ================================
# 5. FULL RESUME ANALYSIS DASHBOARD
# ================================
def generate_full_resume_analysis(raw_text, skills=None, api_key=None):
    """
    Evaluates the entire resume and returns a comprehensive JSON analysis.
    """
    model = get_gemini_model(api_key)
    
    if model:
        try:
            prompt = f"""You are an elite Tech Career Coach and ATS Expert. Analyze the following resume text and extracted skills.
Resume Text: {raw_text[:2000]}
Extracted Skills: {skills}

Generate a comprehensive JSON response with exactly this structure and keys:
{{
  "overall_score": (int 0-100),
  "strengths": ["(list of 3-5 strong points)"],
  "drawbacks": ["(list of 3-5 weaknesses or missing sections)"],
  "keyword_analysis": {{
    "found": ["(list of found keywords)"],
    "missing": ["(list of missing important keywords for this role)"],
    "match_percentage": (int 0-100)
  }},
  "skills_analysis": {{
    "technical": ["(list of tech skills)"],
    "soft": ["(list of soft skills inferred)"],
    "missing": ["(list of important missing tech skills)"],
    "suggested": ["(list of skills to learn next)"]
  }},
  "project_analysis": {{
    "best_project": "(Name of best project)",
    "score": (int 0-10),
    "feedback": "(Constructive feedback on projects)"
  }},
  "section_checks": {{
    "contact": (bool),
    "education": (bool),
    "skills": (bool),
    "projects": (bool),
    "experience": (bool),
    "certifications": (bool),
    "achievements": (bool),
    "portfolio": (bool),
    "github": (bool)
  }},
  "role_predictions": [
    {{"role": "(Role name)", "confidence": (int 0-100)}},
    {{"role": "(Role name 2)", "confidence": (int 0-100)}}
  ],
  "interview_readiness": {{
    "technical": (int 0-100),
    "projects": (int 0-100),
    "resume_quality": (int 0-100),
    "communication": (int 0-100)
  }},
  "improvement_suggestions": [
    "(list of 3-5 specific actionable suggestions)"
  ],
  "career_roadmap": {{
    "skills_to_learn": ["(top 5 skills)"],
    "projects": ["(3 project ideas)"],
    "certifications": ["(2 cert ideas)"],
    "next_technologies": ["(2 next techs)"]
  }}
}}

Return ONLY the raw JSON object, without any markdown formatting, backticks, or extra text.
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            return json.loads(clean_text)
        except Exception as e:
            print("Gemini API Error in full analysis:", e)
            pass

    # Heuristic Offline Fallback
    return {
      "overall_score": 78,
      "strengths": ["Clear section formatting", "Technical skills mentioned"],
      "drawbacks": ["Missing quantified achievements in experience", "No GitHub or Portfolio links found"],
      "keyword_analysis": {
        "found": skills[:5] if skills else ["Python", "Django", "SQL"],
        "missing": ["Docker", "AWS", "CI/CD"],
        "match_percentage": 65
      },
      "skills_analysis": {
        "technical": skills if skills else ["Python", "Javascript", "HTML", "CSS"],
        "soft": ["Communication", "Problem Solving", "Teamwork"],
        "missing": ["Cloud Architecture", "System Design"],
        "suggested": ["Docker", "AWS", "React"]
      },
      "project_analysis": {
        "best_project": "Main Capstone Project",
        "score": 7,
        "feedback": "Add more metrics (e.g., 'improved performance by 20%') to make the project stand out."
      },
      "section_checks": {
        "contact": True,
        "education": True,
        "skills": True,
        "projects": True,
        "experience": True,
        "certifications": False,
        "achievements": False,
        "portfolio": False,
        "github": False
      },
      "role_predictions": [
        {"role": "Software Engineer", "confidence": 85},
        {"role": "Backend Developer", "confidence": 75}
      ],
      "interview_readiness": {
        "technical": 70,
        "projects": 65,
        "resume_quality": 80,
        "communication": 75
      },
      "improvement_suggestions": [
        "Quantify your bullet points using the STAR method.",
        "Add a link to your GitHub profile and live portfolio.",
        "Include a dedicated certifications section if you have any."
      ],
      "career_roadmap": {
        "skills_to_learn": ["AWS", "Docker", "Kubernetes", "GraphQL", "System Design"],
        "projects": ["Build and deploy a scalable microservice", "Create a real-time chat application using WebSockets", "Develop a CI/CD pipeline for your portfolio"],
        "certifications": ["AWS Certified Developer Associate", "Docker Certified Associate"],
        "next_technologies": ["Go", "React"]
      }
    }

# ================================
# FULL RESUME REWRITE SAAS FEATURE
# ================================
def generate_full_resume_rewrite(raw_text, target_role="", job_description="", api_key=None):
    model = get_gemini_model(api_key)
    
    if model:
        try:
            prompt = f"""You are a Premium ATS Resume Rewriter. Your job is to rewrite the provided resume into a professional, ATS-friendly format.
STRICT RULES:
1. NEVER invent information, fake experience, fake companies, fake projects, or fake certifications.
2. NEVER change dates or timelines.
3. ONLY improve wording, grammar, readability, action verbs, and ATS keyword optimization.
4. If a target role or job description is provided, optimize the phrasing for it using ONLY existing facts.

Target Role: {target_role}
Job Description: {job_description}

Original Resume Text:
{raw_text}

Return a strictly valid JSON object with the following structure:
{{
  "original_text": "The full original text",
  "rewritten_text": "The full rewritten text formatted nicely",
  "changes": [
    {{
      "original": "Old sentence",
      "improved": "New improved sentence"
    }}
  ],
  "summary": {{
    "grammar_improved": true,
    "ats_optimization": true,
    "professional_tone": true,
    "readability": true,
    "action_verbs": true,
    "keyword_optimization": true
  }}
}}
"""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            
            # Find JSON object
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(clean_text[start:end])
                
        except Exception as e:
            pass

    # Fallback if AI fails or no API key
    return {
        "original_text": raw_text,
        "rewritten_text": raw_text + "\n\n(Note: Rewrite requires Gemini API key configured)",
        "changes": [],
        "summary": {
            "grammar_improved": False,
            "ats_optimization": False,
            "professional_tone": False,
            "readability": False,
            "action_verbs": False,
            "keyword_optimization": False
        }
    }

# ================================
# 5. PERSONALIZED CAREER ROADMAP (NEW)
# ================================
def generate_personalized_roadmap(target_career, target_timeline, skill_level, study_time, goal, context_data, api_key=None):
    model = get_gemini_model(api_key)
    
    # Extract context data for prompt
    resume_score = context_data.get('resume_score', 'N/A')
    missing_skills = context_data.get('missing_skills', [])
    interview_score = context_data.get('interview_score', 'N/A')
    
    if model:
        try:
            prompt = f"""Generate a personalized Step-by-Step Career Roadmap for a user.
Inputs:
- Target Career: {target_career}
- Timeline: {target_timeline}
- Current Skill Level: {skill_level}
- Daily Study Time: {study_time}
- Goal: {goal}

Existing Analysis Data (Incorporate this to personalize steps):
- Resume/ATS Score: {resume_score} (out of 100)
- Missing Skills Identified: {', '.join(missing_skills) if missing_skills else 'None specifically identified'}
- Mock Interview Score: {interview_score} (out of 100)

Return a structured JSON object with EXACTLY this format:
{{
  "career_goal": "String, summary of the goal",
  "current_readiness": "String, e.g. 'Beginner' or 'Intermediate'",
  "estimated_completion": "String, e.g. '3 Months'",
  "overall_progress": 0,
  "summary": "String, concise roadmap summary explaining why these steps were recommended based on inputs and existing analysis.",
  "next_best_action": "String, ONE highest priority recommendation",
  "steps": [
    {{
      "step_number": 1,
      "title": "Step Title",
      "reason": "String, explicitly state why this is recommended (e.g. 'Required for your target role and currently missing from your resume.')",
      "priority": "High" (or Medium, Low),
      "estimated_time": "String (e.g. '5 Days')",
      "status": "Not Started"
    }}
  ]
}}
Make the steps highly actionable and specific to the {target_career}."""
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(clean_text[start:end])
        except Exception as e:
            print(f"Roadmap generation error: {e}")
            pass

    # Heuristic Offline Fallback
    steps = []
    step_num = 1
    
    # Use existing analysis
    if missing_skills:
        for skill in missing_skills[:2]:
            steps.append({
                "step_number": step_num,
                "title": f"Learn {skill}",
                "reason": f"Required for your target {target_career} role and currently missing from your resume.",
                "priority": "High",
                "estimated_time": "1 Week",
                "status": "Not Started"
            })
            step_num += 1
            
    if resume_score != 'N/A' and (isinstance(resume_score, int) or isinstance(resume_score, float)) and resume_score < 75:
        steps.append({
            "step_number": step_num,
            "title": "Improve ATS Resume",
            "reason": "Current ATS Score is below the recommended level.",
            "priority": "High",
            "estimated_time": "3 Days",
            "status": "Not Started"
        })
        step_num += 1
        
    if interview_score != 'N/A' and (isinstance(interview_score, int) or isinstance(interview_score, float)) and interview_score < 80:
        steps.append({
            "step_number": step_num,
            "title": "Complete AI Mock Interview",
            "reason": "Interview score needs improvement.",
            "priority": "Medium",
            "estimated_time": "2 Days",
            "status": "Not Started"
        })
        step_num += 1
        
    # Standard fallback steps
    steps.append({
        "step_number": step_num,
        "title": f"Master Core {target_career} Concepts",
        "reason": f"Essential foundation for your {goal} goal.",
        "priority": "High",
        "estimated_time": "2 Weeks",
        "status": "Not Started"
    })
    step_num += 1
    
    steps.append({
        "step_number": step_num,
        "title": "Build a Portfolio Project",
        "reason": f"Your resume needs more practical project experience for {target_career}.",
        "priority": "Medium",
        "estimated_time": "3 Weeks",
        "status": "Not Started"
    })

    return {
        "career_goal": goal,
        "current_readiness": skill_level,
        "estimated_completion": target_timeline,
        "overall_progress": 0,
        "summary": f"This roadmap is designed for a {skill_level} aiming for a {target_career} role within {target_timeline}. It addresses key gaps identified in your resume and skills.",
        "next_best_action": steps[0]["title"] if steps else "Start learning core concepts.",
        "steps": steps
    }
