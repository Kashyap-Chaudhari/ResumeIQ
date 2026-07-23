import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import AIInterviewSession, AIInterviewQA
from .services import generate_first_question, evaluate_answer_and_next_question, generate_final_report

@login_required
def coach_ui_view(request):
    return render(request, 'ai_interview/chat.html')

@login_required
@require_http_methods(["POST"])
def api_interview_start(request):
    try:
        data = json.loads(request.body)
        session = AIInterviewSession.objects.create(
            user=request.user,
            role=data.get('role', 'Software Engineer'),
            experience=data.get('experience', ''),
            skills=data.get('skills', ''),
            difficulty=data.get('difficulty', 'Medium'),
            type=data.get('type', 'Mixed'),
            resume_text=data.get('resume_text', ''),
            job_description=data.get('job_description', '')
        )
        
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        first_q = generate_first_question(
            session.role, session.experience, session.skills, 
            session.difficulty, session.type, session.resume_text, 
            session.job_description, api_key=api_key
        )
        
        qa = AIInterviewQA.objects.create(
            session=session,
            question_text=first_q
        )
        
        return JsonResponse({
            "session_id": session.id,
            "question_id": qa.id,
            "question": first_q
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def api_interview_evaluate(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer = data.get('answer', '')
        
        session = get_object_or_404(AIInterviewSession, id=session_id, user=request.user)
        qa = get_object_or_404(AIInterviewQA, id=question_id, session=session)
        
        qa.user_answer = answer
        qa.save()
        
        # Build history
        previous_qas = session.qas.exclude(id=qa.id).order_by('created_at')
        history = [{"question": q.question_text, "answer": q.user_answer} for q in previous_qas if q.user_answer]
        
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        result = evaluate_answer_and_next_question(
            session.role, session.type, session.difficulty, 
            history, qa.question_text, answer, api_key=api_key
        )
        
        qa.evaluation_data = result.get('evaluation', {})
        qa.save()
        
        # Update session stats
        session.total_questions += 1
        eval_data = qa.evaluation_data
        score = eval_data.get('technical_accuracy', 50) # simple heuristic
        session.average_score = ((session.average_score * (session.total_questions - 1)) + score) / session.total_questions
        session.save()
        
        # Create next question
        next_q_text = result.get('next_question', 'Thank you. Do you have any questions for me?')
        next_qa = AIInterviewQA.objects.create(
            session=session,
            question_text=next_q_text
        )
        
        return JsonResponse({
            "evaluation": qa.evaluation_data,
            "next_question_id": next_qa.id,
            "next_question": next_q_text
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def api_interview_report(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(AIInterviewSession, id=session_id, user=request.user)
        session.status = 'completed'
        
        qas = session.qas.order_by('created_at')
        history = [{"question": q.question_text, "answer": q.user_answer} for q in qas if q.user_answer]
        
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        report = generate_final_report(session.role, session.type, history, api_key=api_key)
        session.final_report = report
        session.save()
        
        return JsonResponse({
            "report": report
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# Unused as evaluate handles next question directly
@login_required
@require_http_methods(["POST"])
def api_interview_question(request):
    return JsonResponse({"status": "deprecated, use evaluate instead"})
