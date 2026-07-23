from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('match/', views.job_match_view, name='match'),
    path('tracker/', views.tracker_view, name='tracker'),
    path('resources/', views.resources_view, name='resources'),
    path('tracker/api/applications/', views.api_get_applications, name='api_get_applications'),
    path('tracker/api/applications/add/', views.api_add_application, name='api_add_application'),
    path('tracker/api/applications/<int:app_id>/update/', views.api_update_application, name='api_update_application'),
    path('tracker/api/applications/<int:app_id>/delete/', views.api_delete_application, name='api_delete_application'),
    path('api/google-search/', views.api_google_search, name='api_google_search'),
]
