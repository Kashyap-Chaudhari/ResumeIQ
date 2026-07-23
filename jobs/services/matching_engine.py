import re
from resumes.services.nlp_extractor import extract_skills_from_text
import math
from collections import Counter

def analyze_job_match(resume_text, job_text):
    """
    Computes Job Match Score using scikit-learn TF-IDF + Cosine Similarity,
    detects matching vs missing skills, and provides tailored feedback.
    No LLM used.
    """
    if not resume_text or not job_text:
        raise ValueError("Please provide valid text for both Resume and Job Description.")

    # 1. Cleaning function
    def clean_text(text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s#\+]', ' ', text)  # Keep C++, C# etc.
        return text

    clean_res = clean_text(resume_text)
    clean_job = clean_text(job_text)

    # 2. Extract technical skills to limit the universe of keywords
    jd_skills = set(extract_skills_from_text(job_text))
    
    # 3. Custom TF-IDF Cosine Similarity on full text
    def get_ngrams(text, n=1):
        words = text.split()
        ngrams = []
        for i in range(len(words)-n+1):
            ngrams.append(" ".join(words[i:i+n]))
        return ngrams

    def compute_tfidf_cosine_similarity(text1, text2):
        words1 = text1.split() + get_ngrams(text1, 2)
        words2 = text2.split() + get_ngrams(text2, 2)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "is", "are"}
        words1 = [w for w in words1 if w not in stop_words]
        words2 = [w for w in words2 if w not in stop_words]
        c1 = Counter(words1)
        c2 = Counter(words2)
        all_words = set(c1.keys()).union(set(c2.keys()))
        vec1, vec2 = [], []
        for w in all_words:
            df = sum(1 for c in (c1, c2) if w in c)
            idf = math.log(3 / (1 + df)) + 1
            vec1.append(c1.get(w, 0) * idf)
            vec2.append(c2.get(w, 0) * idf)
        dot = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        norm1 = math.sqrt(sum(v * v for v in vec1))
        norm2 = math.sqrt(sum(v * v for v in vec2))
        if norm1 == 0 or norm2 == 0: return 0.0
        return dot / (norm1 * norm2)

    try:
        similarity = compute_tfidf_cosine_similarity(clean_res, clean_job)
        # Boost similarity slightly for a realistic 0-100 score
        raw_match_score = similarity * 100 * 1.5 
    except Exception:
        raw_match_score = 45.0

    # 4. Custom CountVectorizer for precise Skill Frequencies
    vocab = list(jd_skills)
    if not vocab:
        vocab = ["python", "javascript", "sql", "aws", "docker"] # fallback

    vocab_lower = [v.lower() for v in vocab]
    res_ngrams = clean_res.split() + get_ngrams(clean_res, 2)
    job_ngrams = clean_job.split() + get_ngrams(clean_job, 2)
    c_res = Counter(res_ngrams)
    c_job = Counter(job_ngrams)
    
    counts = [[c_res.get(v, 0) for v in vocab_lower], [c_job.get(v, 0) for v in vocab_lower]]
    
    # counts[0] = resume counts, counts[1] = job counts
    skill_freq = []
    matched_keywords = []
    missing_keywords = []

    for idx, skill in enumerate(vocab):
        j_count = counts[1][idx]
        r_count = counts[0][idx]
        
        if j_count > 0:
            if r_count >= j_count:
                status = "Strong Match"
            elif r_count > 0:
                status = "Weak Match"
            else:
                status = "Missing"
                
            skill_freq.append({
                "keyword": skill,
                "jd_count": int(j_count),
                "resume_count": int(r_count),
                "status": status
            })

            if r_count > 0:
                matched_keywords.append(skill)
            else:
                missing_keywords.append(skill)

    # Sort frequency table by jd_count descending
    skill_freq = sorted(skill_freq, key=lambda x: x['jd_count'], reverse=True)
    
    # Top missing skills
    missing_freqs = [s for s in skill_freq if s['status'] == 'Missing']
    top_missing_skills = [s['keyword'] for s in missing_freqs][:5]

    # 5. Coverage
    total_jd_keywords = len([s for s in skill_freq if s['jd_count'] > 0])
    matched_count = len(matched_keywords)
    coverage_pct = round((matched_count / total_jd_keywords * 100) if total_jd_keywords > 0 else 0)

    # Calculate final blended score
    final_score = int(round((raw_match_score * 0.4) + (coverage_pct * 0.6)))
    final_score = min(100, max(0, final_score))

    # 6. Suggestions
    suggestions = []
    for skill in top_missing_skills[:3]:
        suggestions.append(f"Mention {skill} experience if you genuinely have it.")
    if len(missing_keywords) > 3:
        suggestions.append("Add deployment-related or specialized projects if applicable to cover missing technologies.")
        suggestions.append("Expand project descriptions with relevant technologies already present.")
    if not suggestions:
        suggestions.append("Your resume covers all major keywords. Focus on emphasizing measurable achievements.")

    # 7. Hiring Readiness
    if final_score >= 90:
        readiness = "Excellent Match"
        readiness_desc = "Your resume is highly optimized for this role and passes ATS seamlessly."
    elif final_score >= 75:
        readiness = "Good Match"
        readiness_desc = "Strong candidate, but a few targeted keywords could improve your chances."
    elif final_score >= 50:
        readiness = "Average Match"
        readiness_desc = "You meet some requirements, but significant keyword gaps exist."
    else:
        readiness = "Needs Improvement"
        readiness_desc = "Major gaps detected. Consider rewriting your resume to better align with the job description."

    # 8. Summary
    matched_str = ", ".join(matched_keywords[:4])
    missing_str = ", ".join(top_missing_skills[:3])
    
    if matched_str:
        summary = f"Your resume strongly matches the required {matched_str} skills."
        if missing_str:
            summary += f" The main gaps are {missing_str}. Improving these areas could significantly increase your match score."
    else:
        summary = "Your resume has critical skill gaps compared to the job description."

    return {
        "match_score": final_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "top_missing_skills": top_missing_skills,
        "skill_frequency": skill_freq,
        "coverage_percentage": coverage_pct,
        "suggestions": suggestions,
        "readiness": readiness,
        "readiness_desc": readiness_desc,
        "summary": summary
    }
