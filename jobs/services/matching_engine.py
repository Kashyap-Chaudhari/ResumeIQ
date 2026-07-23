import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resumes.services.nlp_extractor import extract_skills_from_text

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
    
    # 3. TF-IDF Cosine Similarity on full text
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = tfidf_vectorizer.fit_transform([clean_res, clean_job])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Boost similarity slightly for a realistic 0-100 score
        raw_match_score = similarity * 100 * 1.5 
    except Exception:
        raw_match_score = 45.0

    # 4. CountVectorizer for precise Skill Frequencies
    vocab = list(jd_skills)
    if not vocab:
        vocab = ["python", "javascript", "sql", "aws", "docker"] # fallback

    count_vectorizer = CountVectorizer(vocabulary=[v.lower() for v in vocab], ngram_range=(1, 2))
    counts = count_vectorizer.fit_transform([clean_res, clean_job]).toarray()
    
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
