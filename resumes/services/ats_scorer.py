from .nlp_extractor import extract_skills_from_text, extract_action_verbs, extract_metrics_count

def calculate_ats_score(raw_text, parsed_sections=None, skills=None):
    """
    Calculate an ATS Resume Score out of 100 with detailed breakdown and action items.
    Breakdown:
    - Core Skills & Keywords: 30 pts max
    - Quantitative Impact & Metrics: 25 pts max
    - Structure & Section Formatting: 20 pts max
    - Strong Action Verbs: 15 pts max
    - Completeness & Length: 10 pts max
    """
    if not raw_text:
        return 0, {}, ["Empty resume file. Please upload a valid PDF."]

    if skills is None:
        skills = extract_skills_from_text(raw_text)

    action_verbs = extract_action_verbs(raw_text)
    metrics_count = extract_metrics_count(raw_text)
    word_count = len(raw_text.split())

    feedback = []

    # 1. Core Skills & Keywords (Max 30)
    skill_score = min(30, int(len(skills) * 3))
    if skill_score < 18:
        feedback.append("Add more technical industry skills to improve ATS keyword parsing.")
    else:
        feedback.append(f"Strong keyword presence with {len(skills)} technical skills identified.")

    # 2. Quantitative Impact & Metrics (Max 25)
    impact_score = min(25, metrics_count * 5)
    if impact_score < 15:
        feedback.append("Include measurable achievements (e.g. '% increase', 'dollars saved', 'users impacted').")
    else:
        feedback.append(f"Great use of measurable metrics ({metrics_count} instances detected).")

    # 3. Structure & Formatting (Max 20)
    formatting_score = 0
    if parsed_sections:
        has_exp = bool(parsed_sections.get('experience'))
        has_edu = bool(parsed_sections.get('education'))
        has_skills = bool(parsed_sections.get('skills'))
        has_summary = bool(parsed_sections.get('summary'))

        if has_exp: formatting_score += 8
        if has_edu: formatting_score += 5
        if has_skills: formatting_score += 4
        if has_summary: formatting_score += 3
    else:
        formatting_score = 12

    if formatting_score < 15:
        feedback.append("Ensure clear section headers like 'Work Experience', 'Education', and 'Skills'.")

    # 4. Action Verbs (Max 15)
    verb_score = min(15, len(action_verbs) * 3)
    if verb_score < 9:
        feedback.append("Start bullet points with strong power verbs (e.g., 'Spearheaded', 'Optimized', 'Architected').")

    # 5. Completeness & Length (Max 10)
    completeness_score = 0
    if 250 <= word_count <= 1200:
        completeness_score = 10
    elif 150 <= word_count < 250:
        completeness_score = 6
        feedback.append("Your resume is quite short. Aim for 300-800 words for optimal ATS parsing.")
    else:
        completeness_score = 5
        feedback.append("Your resume might be too long. Concise 1-2 page resumes rank highest.")

    total_score = skill_score + impact_score + formatting_score + verb_score + completeness_score
    total_score = max(0, min(100, total_score))

    breakdown = {
        'keywords': skill_score,
        'impact': impact_score,
        'formatting': formatting_score,
        'action_verbs': verb_score,
        'completeness': completeness_score,
        'total': total_score
    }

    return total_score, breakdown, feedback
