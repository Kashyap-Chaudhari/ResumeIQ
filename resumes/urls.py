from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('upload/', views.resume_upload_view, name='upload'),
    path('ai-rewrite/', views.ai_rewrite_feature_view, name='ai_rewrite_feature'),
    path('<int:resume_id>/', views.resume_detail_view, name='detail'),
    path('<int:resume_id>/rewrite/', views.resume_rewrite_view, name='rewrite'),
    path('compare/', views.resume_compare_view, name='compare'),
]
