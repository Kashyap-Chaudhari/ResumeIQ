import os
import tempfile
import docx
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import JobDescription, MatchAnalysis, JobApplication, LearningResource
from resumes.models import Resume
from duckduckgo_search import DDGS
from .services.matching_engine import analyze_job_match
from resumes.services.pdf_parser import extract_text_from_pdf

@login_required
def job_match_view(request):
    if request.method == 'POST':
        job_text = request.POST.get('jd_text', '').strip()
        
        raw_text = ""
        if 'resume_file' in request.FILES:
            uploaded_file = request.FILES['resume_file']
            ext = uploaded_file.name.lower().split('.')[-1]
            
            if ext == 'pdf':
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                raw_text = extract_text_from_pdf(temp_path)
                os.remove(temp_path)
            elif ext == 'docx':
                doc = docx.Document(uploaded_file)
                raw_text = "\n".join([para.text for para in doc.paragraphs])
            elif ext == 'txt':
                raw_text = uploaded_file.read().decode('utf-8', errors='ignore')
            else:
                messages.error(request, 'Unsupported file format. Please upload PDF, DOCX, or TXT.')
                return redirect('jobs:match')
                
        if not raw_text or not job_text:
            messages.error(request, "Please provide both a resume file and a job description.")
            return redirect('jobs:match')

        try:
            # Run TF-IDF Match Analysis
            match_results = analyze_job_match(raw_text, job_text)
            
            return render(request, 'jobs/match.html', {
                'results': match_results,
                'job_text': job_text
            })
            
        except Exception as e:
            messages.error(request, f"Error analyzing job match: {str(e)}")
            return redirect('jobs:match')
            
    return render(request, 'jobs/match.html')

@login_required
def tracker_view(request):
    return render(request, 'jobs/tracker.html')

@login_required
@require_http_methods(["GET"])
def api_get_applications(request):
    apps = JobApplication.objects.filter(user=request.user).order_by('-updated_at')
    data = []
    for app in apps:
        data.append({
            'id': app.id,
            'company_name': app.company_name,
            'job_title': app.job_title,
            'job_type': app.job_type,
            'location': app.location,
            'status': app.status,
            'salary': app.salary,
            'job_link': app.job_link,
            'resume_version': app.resume_version,
            'cover_letter': app.cover_letter,
            'notes': app.notes,
            'application_date': app.application_date.strftime('%Y-%m-%d') if app.application_date else None,
            'updated_at': app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({'applications': data})

@login_required
@require_http_methods(["POST"])
def api_add_application(request):
    try:
        data = json.loads(request.body)
        app = JobApplication.objects.create(
            user=request.user,
            company_name=data.get('company_name', ''),
            job_title=data.get('job_title', ''),
            job_type=data.get('job_type', 'Full-Time'),
            location=data.get('location', ''),
            status=data.get('status', 'Applied'),
            salary=data.get('salary', ''),
            job_link=data.get('job_link', ''),
            resume_version=data.get('resume_version', ''),
            cover_letter=data.get('cover_letter', ''),
            notes=data.get('notes', '')
        )
        return JsonResponse({'success': True, 'id': app.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["PUT", "PATCH"])
def api_update_application(request, app_id):
    try:
        app = JobApplication.objects.get(id=app_id, user=request.user)
        data = json.loads(request.body)
        
        for field in ['company_name', 'job_title', 'job_type', 'location', 'status', 'salary', 'job_link', 'resume_version', 'cover_letter', 'notes']:
            if field in data:
                setattr(app, field, data[field])
                
        app.save()
        return JsonResponse({'success': True})
    except JobApplication.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def api_delete_application(request, app_id):
    try:
        app = JobApplication.objects.get(id=app_id, user=request.user)
        app.delete()
        return JsonResponse({'success': True})
    except JobApplication.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)

@login_required
def resources_view(request):
    latest_match = MatchAnalysis.objects.filter(user=request.user).first()
    missing_skills = latest_match.missing_skills if latest_match else []
    return render(request, 'jobs/resources.html', {'missing_skills': missing_skills})

@login_required
@require_http_methods(["GET"])
def api_google_search(request):
    skill = request.GET.get('skill')
    if not skill:
        return JsonResponse({'error': 'Skill parameter is required'}, status=400)
    
    try:
        query = f"Learn {skill} free tutorial"
        results = []
        with DDGS() as ddgs:
            # We use max_results=10 to get enough to filter from
            for r in ddgs.text(query, max_results=10):
                # Basic trusted domains filtering (optional, but requested)
                trusted = any(x in r['href'].lower() for x in ['docs', 'learn', 'freecodecamp', 'mdn', 'w3schools', 'geeksforgeeks', 'roadmap.sh', 'codecademy', 'coursera', 'edx', 'udemy', 'digitalocean', 'redhat', 'mozilla', 'oracle', 'aws', 'cloud.google'])
                
                # If we want to prioritize trusted, we can just grab the first 5-10
                results.append({
                    'title': r.get('title', ''),
                    'body': r.get('body', ''),
                    'url': r.get('href', ''),
                    'trusted': trusted
                })
        
        # Sort so trusted are first
        results.sort(key=lambda x: x['trusted'], reverse=True)
        # Return top 5
        return JsonResponse({'skill': skill, 'results': results[:5]})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
