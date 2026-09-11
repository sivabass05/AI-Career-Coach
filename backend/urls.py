from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from backend import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
    'admin-dashboard/',
    views.admin_dashboard,
    name='admin_dashboard'
),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('skill-assessment/', views.skill_assessment, name='skill_assessment'),
    path('career-recommendation/', views.career_recommendation, name='career_recommendation'),
    path('recommend-career/', views.recommend_career, name='recommend_career'),
    path('learning-path/', views.learning_path, name='learning_path'),
    path(
    'learning-path/complete/',
    views.complete_learning_step,
    name='complete_learning_step'
),
    path('resume/', views.resume_view, name='resume'),
    path('mock-interview/', views.mock_interview, name='mock_interview'),
    path('interview-result/', views.interview_result, name='interview_result'),
    path('job-recommendation/', views.job_recommendation, name='job_recommendation'),
    path(
    'share-career-profile/',
    views.share_career_profile,
    name='share_career_profile'
),
    path(
    'gemini-test/',
    views.gemini_test,
    name='gemini_test'
),

    # Shareable Career Profile
    path(
        'career-profile/<uuid:token>/',
        views.public_career_profile,
        name='public_career_profile'
    ),
]


# ------------------------------------------------------------
# MEDIA FILES
# ------------------------------------------------------------

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )