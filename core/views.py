from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages
from .models import UserProfile
from resumes.models import Resume
from jobs.models import JobApplication

def global_context_processor(request):
    context = {}
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            context['user_profile'] = profile
            context['user_theme'] = profile.theme_preference
        else:
            context['user_theme'] = 'dark'
    return context

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Registration successful. Welcome to ResumeIQ!")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                remember_me = form.cleaned_data.get('remember_me')
                if not remember_me:
                    request.session.set_expiry(0) # Expire on browser close
                else:
                    request.session.set_expiry(2592000) # 30 days
                    
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    # Gather analytics
    user = request.user
    resumes = Resume.objects.filter(user=user).order_by('-updated_at')
    applications = JobApplication.objects.filter(user=user)
    
    recent_resume = resumes.first()
    
    app_stats = {
        'saved': applications.filter(status='saved').count(),
        'applied': applications.filter(status='applied').count(),
        'interviewing': applications.filter(status='interviewing').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    readiness = None
    if hasattr(user, 'readiness'):
        readiness = user.readiness
        
    context = {
        'recent_resume': recent_resume,
        'app_stats': app_stats,
        'total_apps': applications.count(),
        'readiness': readiness
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update settings
        api_key = request.POST.get('gemini_api_key')
        theme = request.POST.get('theme_preference')
        
        if api_key is not None:
            profile.gemini_api_key = api_key
        if theme in dict(UserProfile.THEME_CHOICES):
            profile.theme_preference = theme
            
        profile.save()
        messages.success(request, "Profile settings updated successfully.")
        return redirect('profile')
        
    return render(request, 'core/profile.html', {'profile': profile})

@login_required
def analytics_view(request):
    user = request.user
    applications = JobApplication.objects.filter(user=user)
    
    app_stats = {
        'saved': applications.filter(status='saved').count(),
        'applied': applications.filter(status='applied').count(),
        'interviewing': applications.filter(status='interviewing').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    context = {
        'app_stats': app_stats,
    }
    return render(request, 'core/analytics.html', context)
