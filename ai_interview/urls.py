from django.urls import path
from . import views

app_name = 'ai_interview'

urlpatterns = [
    path('', views.coach_ui_view, name='coach_ui'),
    path('api/interview/start', views.api_interview_start, name='api_interview_start'),
    path('api/interview/question', views.api_interview_question, name='api_interview_question'),
    path('api/interview/evaluate', views.api_interview_evaluate, name='api_interview_evaluate'),
    path('api/interview/report', views.api_interview_report, name='api_interview_report'),
]
