import uuid

from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    education = models.CharField(max_length=150, blank=True)
    college = models.CharField(max_length=200, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    career_goal = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    share_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    is_profile_shared = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username


class UserSkillAssessment(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    selected_skills = models.TextField(
        blank=True
    )

    skill_levels = models.JSONField(
        default=dict,
        blank=True
    )

    career_interest = models.CharField(
        max_length=150,
        blank=True
    )

    enjoyed_field = models.CharField(
        max_length=150,
        blank=True
    )

    skill_score = models.IntegerField(
        default=0
    )

    recommended_career = models.CharField(
        max_length=150,
        default='Not Assessed'
    )

    # Learning progress percentage
    learning_progress = models.IntegerField(
        default=0
    )

    # Example: [1, 2, 3]
    completed_learning_steps = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - Skill Assessment"


class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    ats_score = models.IntegerField(default=0)
    detected_skills = models.TextField(blank=True)
    ai_analysis = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"


class MockInterview(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    career = models.CharField(
        max_length=100
    )

    question = models.TextField()

    answer = models.TextField()

    # Final weighted score
    score = models.IntegerField(
        default=0
    )

    # Saved Gemini category scores.
    # The Interview Result page reads these fields directly.
    technical_score = models.IntegerField(
        default=0
    )

    relevance_score = models.IntegerField(
        default=0
    )

    communication_score = models.IntegerField(
        default=0
    )

    # Saved AI feedback data.
    strengths = models.TextField(
        blank=True
    )

    improvements = models.TextField(
        blank=True
    )

    better_answer_tip = models.TextField(
        blank=True
    )

    feedback = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.career}"
