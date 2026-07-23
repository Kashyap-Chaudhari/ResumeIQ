from django.urls import path
from . import views

app_name = 'coaching'

urlpatterns = [
    path('interview/', views.interview_prep_view, name='interview'),
    path('readiness/', views.readiness_view, name='readiness'),
    path('api/placement-readiness/', views.api_readiness_data, name='api_readiness_data'),
    path('roadmap/', views.roadmap_view, name='roadmap'),
    path('api/career-roadmap/', views.api_generate_career_roadmap, name='api_career_roadmap'),
    path('export/', views.export_report_view, name='export_report'),
]
