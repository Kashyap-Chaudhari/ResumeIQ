import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Resume
from .services.pdf_parser import extract_text_from_pdf, parse_resume_sections
from .services.nlp_extractor import extract_skills_from_text
from .services.ats_scorer import calculate_ats_score


@login_required
def resume_upload_view(request):
    if request.method == 'POST':
        if 'resume_file' not in request.FILES:
            messages.error(request, 'Please upload a PDF file.')
            return redirect('resumes:upload')
            
        uploaded_file = request.FILES['resume_file']
        title = request.POST.get('title', uploaded_file.name)
        
        # Save the file temporarily or directly via model
        resume = Resume.objects.create(
            user=request.user,
            title=title,
            file=uploaded_file
        )
        
        # Process the resume
        try:
            try:
                raw_text = extract_text_from_pdf(resume.file.path)
            except Exception:
                raw_text = extract_text_from_pdf(uploaded_file)
            
            # 2. Parse Sections
            sections = parse_resume_sections(raw_text)
            
            # 3. Extract Skills
            skills = extract_skills_from_text(raw_text)
            
            # 4. Calculate ATS Score
            total_score, breakdown, action_items = calculate_ats_score(raw_text, sections, skills)
            
            # 5. Full AI Analysis Dashboard
            from coaching.services.ai_engine import generate_full_resume_analysis
            api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
            ai_analysis = generate_full_resume_analysis(raw_text, skills, api_key=api_key)
            
            # Update Resume Object
            resume.raw_text = raw_text
            resume.ats_score = total_score
            resume.parsed_skills = skills
            resume.parsed_sections = sections
            resume.ats_breakdown = breakdown
            resume.ats_feedback = action_items
            resume.ai_analysis = ai_analysis
            resume.save()
            
            messages.success(request, f'Successfully analyzed {title}!')
            return redirect('resumes:detail', resume_id=resume.id)
            
        except Exception as e:
            messages.error(request, f'Error processing resume: {str(e)}')
            
    return render(request, 'resumes/upload.html')

@login_required
def resume_detail_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Render the detailed report
    return render(request, 'resumes/detail.html', {'resume': resume})

@login_required
def resume_rewrite_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    if request.method == 'POST':
        # Need to call AI Engine to rewrite bullet points
        from coaching.services.ai_engine import generate_resume_rewrite
        
        bullet_points = request.POST.get('bullet_points', '')
        target_job = request.POST.get('target_job', '')
        
        # Fallback to empty context if missing
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        # Use AI engine
        try:
            rewritten_bullets = generate_resume_rewrite(
                bullet_points, target_job, api_key=api_key
            )
            return render(request, 'resumes/rewriter.html', {
                'resume': resume,
                'original': bullet_points,
                'target': target_job,
                'rewritten': rewritten_bullets
            })
        except Exception as e:
            messages.error(request, f"AI generation failed: {str(e)}")
            
    return render(request, 'resumes/rewriter.html', {'resume': resume})

@login_required
def resume_compare_view(request):
    # Select two resumes to compare versions
    resumes = Resume.objects.filter(user=request.user)
    if request.method == 'POST':
        r1_id = request.POST.get('resume1')
        r2_id = request.POST.get('resume2')
        if r1_id and r2_id:
            r1 = get_object_or_404(Resume, id=r1_id, user=request.user)
            r2 = get_object_or_404(Resume, id=r2_id, user=request.user)
            return render(request, 'resumes/compare.html', {'resumes': resumes, 'r1': r1, 'r2': r2})
            
    return render(request, 'resumes/compare.html', {'resumes': resumes})

@login_required
def ai_rewrite_feature_view(request):
    if request.method == 'POST':
        from coaching.services.ai_engine import generate_full_resume_rewrite
        
        target_role = request.POST.get('target_role', '')
        job_description = request.POST.get('job_description', '')
        pasted_text = request.POST.get('pasted_text', '').strip()
        
        raw_text = ""
        
        if pasted_text:
            raw_text = pasted_text
        elif 'resume_file' in request.FILES:
            uploaded_file = request.FILES['resume_file']
            # Basic parsing. For a robust app, use docx parser etc.
            if uploaded_file.name.endswith('.pdf'):
                # We need to save it temporarily to use extract_text_from_pdf
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                raw_text = extract_text_from_pdf(temp_path)
                os.remove(temp_path)
            elif uploaded_file.name.endswith('.txt'):
                raw_text = uploaded_file.read().decode('utf-8')
            else:
                messages.error(request, 'Unsupported file format. Please upload PDF, TXT or paste your text.')
                return redirect('resumes:ai_rewrite_feature')
        
        if not raw_text:
            messages.error(request, 'Please provide resume text via upload or paste.')
            return redirect('resumes:ai_rewrite_feature')
            
        api_key = request.user.userprofile.gemini_api_key if hasattr(request.user, 'userprofile') else None
        
        try:
            ai_result = generate_full_resume_rewrite(raw_text, target_role, job_description, api_key=api_key)
            return render(request, 'resumes/ai_rewrite.html', {
                'ai_result': ai_result,
                'target_role': target_role,
                'job_description': job_description
            })
        except Exception as e:
            messages.error(request, f"AI generation failed: {str(e)}")
            return redirect('resumes:ai_rewrite_feature')

    return render(request, 'resumes/ai_rewrite.html')
