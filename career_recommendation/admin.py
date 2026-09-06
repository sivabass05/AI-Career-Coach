from django.contrib import admin

from .models import (
    StudentProfile,
    UserSkillAssessment,
    Resume,
    MockInterview,
)


# =========================================================
# STUDENT PROFILE
# =========================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "phone",
        "education",
        "college",
        "graduation_year",
        "career_goal",
        "created_at",
    )

    search_fields = (
        "user__username",
        "full_name",
        "phone",
        "education",
        "college",
        "career_goal",
    )

    list_filter = (
        "graduation_year",
    )


# =========================================================
# USER SKILL ASSESSMENT
# =========================================================

@admin.register(UserSkillAssessment)
class UserSkillAssessmentAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "career_interest",
        "enjoyed_field",
        "skill_score",
        "recommended_career",
        "created_at",
    )

    search_fields = (
        "user__username",
        "career_interest",
        "enjoyed_field",
        "recommended_career",
        "selected_skills",
    )

    list_filter = (
        "career_interest",
        "recommended_career",
    )


# =========================================================
# RESUME
# =========================================================

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "resume_file",
        "ats_score",
        "uploaded_at",
    )

    search_fields = (
        "user__username",
        "detected_skills",
    )

    list_filter = (
        "ats_score",
        "uploaded_at",
    )


# =========================================================
# MOCK INTERVIEW
# =========================================================

@admin.register(MockInterview)
class MockInterviewAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "career",
        "score",
        "created_at",
    )

    search_fields = (
        "user__username",
        "career",
        "question",
        "answer",
        "feedback",
    )

    list_filter = (
        "career",
        "score",
        "created_at",
    )