import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import InterviewSession, PlacementReadiness, CareerRoadmap
from .services.ai_engine import generate_interview_questions, evaluate_interview_answer, generate_career_roadmap, generate_personalized_roadmap
from .services.pdf_report import generate_html_report
from resumes.models import Resume
from jobs.models import MatchAnalysis
try:
    from ai_interview.models import AIInterviewSession
except ImportError:
    AIInterviewSession = None

@login_required
def interview_prep_view(request):
    if request.method == 'POST':
        # Either start a session or submit an answer
        action = request.POST.get('action')
        
        if action == 'start':
            target_role = request.POST.get('target_role')
            session = InterviewSession.objects.create(
                user=request.user,
                target_role=target_role
            )
            
            
            api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
            
            try:
                questions_json = generate_interview_questions(target_role, api_key=api_key)
                questions_data = json.loads(questions_json)
                session.questions_json = questions_data.get('questions', [])
                session.save()
                return render(request, 'coaching/interview.html', {'session': session, 'current_q': 0})
            except Exception as e:
                messages.error(request, f"Failed to generate questions: {str(e)}")
                return redirect('coaching:interview')
                
        elif action == 'submit_answer':
            session_id = request.POST.get('session_id')
            q_index = int(request.POST.get('q_index', 0))
            answer = request.POST.get('answer')
            
            session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
            
            
            api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
            
            try:
                question_text = session.questions_json[q_index]['question']
                score, feedback_text = evaluate_interview_answer(question_text, answer, api_key=api_key)
                feedback = f"Score: {score}/100. {feedback_text}"
                
                # Update feedback
                if not session.feedback_json:
                    session.feedback_json = []
                session.feedback_json.append({
                    'question': question_text,
                    'answer': answer,
                    'feedback': feedback
                })
                session.save()
                
                next_q = q_index + 1
                if next_q < len(session.questions_json):
                    return render(request, 'coaching/interview.html', {'session': session, 'current_q': next_q, 'last_feedback': feedback})
                else:
                    session.is_completed = True
                    session.save()
                    return render(request, 'coaching/interview.html', {'session': session, 'completed': True})
            except Exception as e:
                messages.error(request, f"Error evaluating answer: {str(e)}")
                
    return render(request, 'coaching/interview.html')

@login_required
def readiness_view(request):
    readiness, created = PlacementReadiness.objects.get_or_create(user=request.user)
    return render(request, 'coaching/readiness.html', {'readiness': readiness})

@login_required
def roadmap_view(request):
    roadmaps = CareerRoadmap.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        target_role = request.POST.get('target_role')
        current_level = request.POST.get('current_level')
        
        
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        try:
            roadmap_json = generate_career_roadmap(target_role, current_level, api_key=api_key)
            roadmap_data = roadmap_json # because it returns list directly in heuristic
            
            roadmap = CareerRoadmap.objects.create(
                user=request.user,
                target_role=target_role,
                current_level=current_level,
                roadmap_json=roadmap_data.get('steps', [])
            )
            messages.success(request, f"Generated roadmap for {target_role}")
            return redirect('coaching:roadmap')
        except Exception as e:
            messages.error(request, f"Error generating roadmap: {str(e)}")
            
    return render(request, 'coaching/roadmap.html', {'roadmaps': roadmaps})

@login_required
def export_report_view(request):
    resume_id = request.GET.get('resume_id')
    if resume_id:
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        readiness = getattr(request.user, 'readiness', None)
        
        html_string = generate_html_report(resume, readiness=readiness)
        
        response = HttpResponse(html_string, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="ResumeIQ_Report_{resume.id}.html"'
        return response
    
    return redirect('dashboard')


@login_required
def api_readiness_data(request):
    data = {
        'resume_score': None,
        'ats_score': None,
        'job_match_score': None,
        'interview_score': None,
        'missing_skills': [],
        'strengths': [],
        'weaknesses': [],
        'action_plan': [],
        'checklist': {
            'resume_uploaded': False,
            'resume_analyzed': False,
            'ats_checked': False,
            'job_matched': False,
            'interview_completed': False
        }
    }
    
    # 1. Resume & ATS
    latest_resume = Resume.objects.filter(user=request.user).order_by('-updated_at').first()
    if latest_resume:
        data['checklist']['resume_uploaded'] = True
        data['checklist']['resume_analyzed'] = bool(latest_resume.parsed_sections)
        data['checklist']['ats_checked'] = latest_resume.ats_score > 0
        
        data['ats_score'] = latest_resume.ats_score
        # Calculate a basic Resume Score based on completeness of parsed sections
        sections = latest_resume.parsed_sections or {}
        num_sections = len([k for k, v in sections.items() if v])
        data['resume_score'] = min(100, num_sections * 25) # e.g. 4 sections = 100
        
        # Add ATS strengths/weaknesses
        for item in latest_resume.ats_feedback:
            if 'improve' in item.lower() or 'missing' in item.lower() or 'low' in item.lower():
                data['weaknesses'].append(item)
            else:
                data['strengths'].append(item)
                
    # 2. Job Match
    latest_match = MatchAnalysis.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_match:
        data['checklist']['job_matched'] = True
        data['job_match_score'] = latest_match.match_score
        data['missing_skills'] = latest_match.missing_skills
        
        for skill in latest_match.matching_skills:
            data['strengths'].append(f"Strong match for skill: {skill}")
        for skill in latest_match.missing_skills:
            data['weaknesses'].append(f"Missing required skill: {skill}")
            
    # 3. AI Interview
    if AIInterviewSession:
        latest_interview = AIInterviewSession.objects.filter(user=request.user, status='completed').order_by('-created_at').first()
        if latest_interview:
            data['checklist']['interview_completed'] = True
            data['interview_score'] = latest_interview.average_score
            if latest_interview.final_report:
                data['strengths'].extend(latest_interview.final_report.get('strengths', []))
                data['weaknesses'].extend(latest_interview.final_report.get('weaknesses', []))
                data['action_plan'].extend(latest_interview.final_report.get('areas_to_improve', []))

    # Calculate Overall Score
    weights = {'resume': 25, 'ats': 20, 'match': 25, 'interview': 20, 'skills': 10}
    total_weight = 0
    total_score = 0
    
    if data['resume_score'] is not None:
        total_score += data['resume_score'] * weights['resume']
        total_weight += weights['resume']
    if data['ats_score'] is not None:
        total_score += data['ats_score'] * weights['ats']
        total_weight += weights['ats']
    if data['job_match_score'] is not None:
        total_score += data['job_match_score'] * weights['match']
        total_weight += weights['match']
    if data['interview_score'] is not None:
        total_score += data['interview_score'] * weights['interview']
        total_weight += weights['interview']
        
    skills_score = 0
    if data['checklist']['job_matched']:
        skills_score = max(0, 100 - (len(data['missing_skills']) * 15))
        total_score += skills_score * weights['skills']
        total_weight += weights['skills']
        
    overall_score = 0
    if total_weight > 0:
        overall_score = round(total_score / total_weight)
        
    data['overall_score'] = overall_score
    data['skills_score'] = skills_score if data['checklist']['job_matched'] else None
    
    # Generate Action Plan dynamically from missing items
    if not data['checklist']['resume_uploaded']:
        data['action_plan'].append("Upload your first resume to get started.")
    elif not data['checklist']['job_matched']:
        data['action_plan'].append("Run a Job Match analysis to see how you compare to target roles.")
    
    for skill in data['missing_skills'][:3]:
        data['action_plan'].append(f"Learn and practice: {skill}")
        
    if data['ats_score'] is not None and data['ats_score'] < 70:
        data['action_plan'].append("Improve your ATS formatting and keywords.")
        
    if not data['checklist']['interview_completed']:
        data['action_plan'].append("Complete a Mock Interview with the AI Coach.")
        
    # Deduplicate lists
    data['strengths'] = list(set(data['strengths']))[:5]
    data['weaknesses'] = list(set(data['weaknesses']))[:5]
    data['action_plan'] = list(dict.fromkeys(data['action_plan']))[:5]
    
    # Summary string
    summary = f"Your overall readiness is {overall_score}%."
    if data['ats_score'] and data['ats_score'] > 75:
        summary += " Your resume has strong ATS compatibility."
    elif data['ats_score']:
        summary += " Your resume needs ATS optimization."
        
    if data['missing_skills']:
        summary += f" The biggest improvement areas are {', '.join(data['missing_skills'][:3])}."
        
    data['summary'] = summary
    
    return JsonResponse(data)

@login_required
def api_generate_career_roadmap(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        body = json.loads(request.body)
        target_career = body.get('target_career')
        target_timeline = body.get('target_timeline')
        skill_level = body.get('skill_level')
        study_time = body.get('study_time')
        goal = body.get('goal')
        
        # 1. Collect Context Data
        context_data = {}
        
        latest_resume = Resume.objects.filter(user=request.user).order_by('-updated_at').first()
        if latest_resume:
            context_data['resume_score'] = latest_resume.ats_score
            
        latest_match = MatchAnalysis.objects.filter(user=request.user).order_by('-created_at').first()
        if latest_match:
            context_data['missing_skills'] = latest_match.missing_skills
            
        if AIInterviewSession:
            latest_interview = AIInterviewSession.objects.filter(user=request.user, status='completed').order_by('-created_at').first()
            if latest_interview:
                context_data['interview_score'] = latest_interview.average_score

        # 2. Call AI Engine
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        roadmap_data = generate_personalized_roadmap(
            target_career=target_career,
            target_timeline=target_timeline,
            skill_level=skill_level,
            study_time=study_time,
            goal=goal,
            context_data=context_data,
            api_key=api_key
        )
        
        # 3. Save to database
        # Re-using the CareerRoadmap model, saving into milestones field
        roadmap = CareerRoadmap.objects.create(
            user=request.user,
            target_role=target_career,
            current_level=skill_level,
            milestones=roadmap_data
        )
        
        return JsonResponse({'success': True, 'roadmap': roadmap_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
