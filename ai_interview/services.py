import os
import json
import google.generativeai as genai

def get_genai_model(api_key=None):
    key = api_key or os.environ.get('GEMINI_API_KEY')
    if not key:
        raise ValueError("No Gemini API key found.")
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_first_question(role, experience, skills, difficulty, interview_type, resume_text, job_description, api_key=None):
    model = get_genai_model(api_key)
    prompt = f"""
    You are an expert technical and HR interviewer. Start an interview for the following candidate:
    Role: {role}
    Experience: {experience}
    Skills: {skills}
    Difficulty: {difficulty}
    Interview Type: {interview_type}
    
    Resume Context: {resume_text[:1000] if resume_text else 'None'}
    Job Description Context: {job_description[:1000] if job_description else 'None'}
    
    Generate the FIRST interview question dynamically.
    Do NOT use standard cliché questions. Make it highly relevant to the provided context.
    Return ONLY a valid JSON object in this exact format, with no markdown formatting or backticks:
    {{
        "question": "Your question here"
    }}
    """
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())['question']
    except Exception as e:
        return f"Could you tell me about your experience with {skills.split(',')[0] if skills else role}?"

def evaluate_answer_and_next_question(role, type, difficulty, history, current_question, user_answer, api_key=None):
    model = get_genai_model(api_key)
    history_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in history])
    prompt = f"""
    You are an expert interviewer for a {role} position. ({type} Interview, {difficulty} difficulty).
    Evaluate the candidate's answer to the current question, and then generate the next follow-up or new question.
    
    History of Q&A so far:
    {history_text}
    
    Current Question: {current_question}
    Candidate's Answer: {user_answer}
    
    Return ONLY a valid JSON object (no markdown, no backticks) with the following structure:
    {{
        "evaluation": {{
            "confidence_score": 0-100,
            "communication_score": 0-100,
            "technical_accuracy": 0-100,
            "problem_solving": 0-100,
            "clarity": 0-100,
            "completeness": 0-100,
            "grammar": 0-100,
            "professionalism": 0-100,
            "suggestions_for_improvement": "Detailed advice",
            "ideal_answer": "How they should have answered",
            "key_points_missed": ["Point 1", "Point 2"],
            "better_way_to_answer": "A more concise or structured way to say it",
            "overall_feedback": "A summary of their performance on this question"
        }},
        "next_question": "Your next intelligent, adaptive question based on their answer and history."
    }}
    """
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        raise ValueError(f"Failed to parse AI response: {str(e)}")

def generate_final_report(role, type, history, api_key=None):
    model = get_genai_model(api_key)
    history_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in history])
    prompt = f"""
    You are an expert technical and HR interviewer. The interview for a {role} position ({type}) is now complete.
    Here is the full transcript:
    {history_text}
    
    Generate a comprehensive Final Interview Report.
    Return ONLY a valid JSON object (no markdown, no backticks) with this structure:
    {{
        "overall_interview_score": 0-100,
        "communication": 0-100,
        "technical_knowledge": 0-100,
        "confidence": 0-100,
        "problem_solving": 0-100,
        "behavioral_skills": 0-100,
        "leadership": 0-100,
        "grammar": 0-100,
        "professionalism": 0-100,
        "strengths": ["Strength 1", "Strength 2"],
        "weaknesses": ["Weakness 1", "Weakness 2"],
        "areas_to_improve": ["Area 1", "Area 2"],
        "recommended_learning_topics": ["Topic 1", "Topic 2"],
        "interview_readiness": "Not Ready / Needs Practice / Ready / Highly Recommended",
        "hiring_recommendation": "Strong No / No / Neutral / Yes / Strong Yes"
    }}
    """
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        raise ValueError(f"Failed to parse AI response: {str(e)}")
