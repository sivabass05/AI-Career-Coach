from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from backend import views


urlpatterns = [

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    path(
        "admin/",
        admin.site.urls
    ),


    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    path(
        "",
        views.home,
        name="home"
    ),


    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),


    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    path(
        "profile/",
        views.profile,
        name="profile"
    ),


    # --------------------------------------------------------
    # SKILL ASSESSMENT
    # --------------------------------------------------------

    path(
        "skill-assessment/",
        views.skill_assessment,
        name="skill_assessment"
    ),


    # --------------------------------------------------------
    # CAREER RECOMMENDATION
    # --------------------------------------------------------

    path(
        "career-recommendation/",
        views.career_recommendation,
        name="career_recommendation"
    ),

    path(
        "recommend-career/",
        views.recommend_career,
        name="recommend_career"
    ),


    # --------------------------------------------------------
    # LEARNING PATH
    # --------------------------------------------------------

    path(
        "learning-path/",
        views.learning_path,
        name="learning_path"
    ),


    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    path(
        "resume/",
        views.resume_view,
        name="resume"
    ),


    # --------------------------------------------------------
    # MOCK INTERVIEW
    # --------------------------------------------------------

    path(
        "mock-interview/",
        views.mock_interview,
        name="mock_interview"
    ),

    path(
        "interview-result/",
        views.interview_result,
        name="interview_result"
    ),


    # --------------------------------------------------------
    # JOB RECOMMENDATION
    # --------------------------------------------------------

    path(
        "job-recommendation/",
        views.job_recommendation,
        name="job_recommendation"
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