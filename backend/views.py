from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
import json

from career_recommendation.models import (
    StudentProfile,
    UserSkillAssessment,
    Resume,
    MockInterview,
)

import re


# =========================================================
# HOME
# =========================================================

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, "home.html")


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        education = request.POST.get("education", "").strip()
        college = request.POST.get("college", "").strip()
        graduation_year = request.POST.get("graduation_year", "").strip()
        career_goal = request.POST.get("career_goal", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Required fields
        if not full_name or not username or not email or not password:
            messages.error(
                request,
                "Please fill all required fields."
            )
            return render(request, "register.html")

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return render(request, "register.html")

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "Email already registered."
            )
            return render(request, "register.html")

        # Password check
        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return render(request, "register.html")

        if len(password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters."
            )
            return render(request, "register.html")

        user = None

        try:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            user.first_name = full_name
            user.save()

            year = None

            if graduation_year:
                try:
                    year = int(graduation_year)
                except ValueError:
                    year = None

            StudentProfile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                education=education,
                college=college,
                graduation_year=year,
                career_goal=career_goal
            )

            messages.success(
                request,
                "Registration successful. Please login."
            )

            return redirect("login")

        except Exception as e:

            if user:
                user.delete()

            messages.error(
                request,
                f"Registration failed: {str(e)}"
            )

    return render(request, "register.html")


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(request, "login.html")


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    assessment = None
    resume = None
    profile = None

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        assessment = None

    try:
        resume = Resume.objects.get(
            user=request.user
        )
    except Resume.DoesNotExist:
        resume = None

    try:
        profile = StudentProfile.objects.get(
            user=request.user
        )
    except StudentProfile.DoesNotExist:
        profile = None

    # Skill score
    skill_score = 0

    if assessment:
        skill_score = assessment.skill_score or 0

    # Career recommendation
    recommended_career = ""

    if assessment:
        recommended_career = assessment.recommended_career or ""

    # Career match
    career_match = skill_score

    # Interview score
    interview_score = 0

    interviews = MockInterview.objects.filter(
        user=request.user
    )

    if interviews.exists():

        total = sum(
            interview.score
            for interview in interviews
        )

        interview_score = round(
            total / interviews.count()
        )

    # Resume score
    resume_score = 0

    if resume:
        resume_score = resume.ats_score or 0

    context = {
        "skill_score": skill_score,
        "career_match": career_match,
        "recommended_career": recommended_career,
        "interview_score": interview_score,
        "resume_score": resume_score,
        "profile": profile,
        "assessment": assessment,
        "resume": resume,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile(request):

    try:
        profile = StudentProfile.objects.get(
            user=request.user
        )
    except StudentProfile.DoesNotExist:

        profile = StudentProfile.objects.create(
            user=request.user,
            full_name=(
                request.user.get_full_name()
                or request.user.username
            )
        )

    if request.method == "POST":

        profile.full_name = request.POST.get(
            "full_name",
            profile.full_name
        )

        profile.phone = request.POST.get(
            "phone",
            profile.phone
        )

        profile.education = request.POST.get(
            "education",
            profile.education
        )

        profile.college = request.POST.get(
            "college",
            profile.college
        )

        graduation_year = request.POST.get(
            "graduation_year",
            ""
        )

        if graduation_year:
            try:
                profile.graduation_year = int(
                    graduation_year
                )
            except ValueError:
                pass

        profile.career_goal = request.POST.get(
            "career_goal",
            profile.career_goal
        )

        profile.save()

        # Update User first name
        request.user.first_name = profile.full_name
        request.user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "profile.html",
        {
            "profile": profile
        }
    )


# =========================================================
# SKILL ASSESSMENT
# =========================================================

@login_required(login_url='login')
def skill_assessment(request):

    assessment, created = UserSkillAssessment.objects.get_or_create(
        user=request.user
    )

    show_result = False

    if request.method == 'POST':

        print("===== SKILL ASSESSMENT POST =====")
        print(request.POST)

        # =====================================================
        # SELECTED SKILLS
        # =====================================================

        skills = request.POST.getlist(
            'selected_skills'
        )

        # =====================================================
        # GET SKILL LEVELS
        # =====================================================

        skill_levels = {}

        skill_levels_raw = request.POST.get(
            'skill_levels',
            ''
        ).strip()

        if skill_levels_raw:

            try:
                skill_levels = json.loads(
                    skill_levels_raw
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):
                skill_levels = {}

        # =====================================================
        # BACKUP METHOD
        # =====================================================

        if not skill_levels:

            for key, value in request.POST.items():

                if (
                    key.startswith('skill_level_')
                    and value.strip()
                ):

                    skill_name = key.replace(
                        'skill_level_',
                        '',
                        1
                    )

                    skill_levels[skill_name] = (
                        value.strip()
                    )

        # =====================================================
        # CAREER INTEREST
        # =====================================================

        career_interest = request.POST.get(
            'career_interest',
            ''
        ).strip()

        # =====================================================
        # ENJOYED FIELD
        # =====================================================

        enjoyed_field = request.POST.get(
            'enjoyed_field',
            ''
        ).strip()

        # =====================================================
        # CONVERT SKILLS TO STRING
        # =====================================================

        skills_str = ", ".join(
            skills
        )

        total_skills_count = len(
            skills
        )

        # =====================================================
        # SKILL SCORE
        # =====================================================

        if total_skills_count > 0:

            calculated_score = min(
                total_skills_count * 15 + 25,
                95
            )

        else:

            calculated_score = 0

        # =====================================================
        # CAREER RECOMMENDATION
        # =====================================================

        recommendation = (
            career_interest
            if career_interest
            else "Full Stack Developer"
        )

        # =====================================================
        # SAVE ASSESSMENT
        # =====================================================

        assessment.selected_skills = (
            skills_str
        )

        assessment.skill_levels = (
            skill_levels
        )

        assessment.career_interest = (
            career_interest
        )

        assessment.enjoyed_field = (
            enjoyed_field
        )

        assessment.skill_score = (
            calculated_score
        )

        assessment.recommended_career = (
            recommendation
        )

        assessment.save()

        show_result = True

        messages.success(
            request,
            'Skill assessment saved successfully!'
        )

    # =========================================================
    # RENDER PAGE
    # =========================================================

    return render(
        request,
        'skill-assessment.html',
        {
            'assessment': assessment,
            'show_result': show_result
        }
    )


# =========================================================
# CAREER RECOMMENDATION PAGE
# =========================================================

@login_required(login_url='login')
def career_recommendation(request):

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )

    except UserSkillAssessment.DoesNotExist:

        return render(
            request,
            'career-recommendation.html',
            {
                'assessment': None,
                'recommendations': [],
                'career': '',
                'career_info': {}
            }
        )

    # Get student skills
    selected_skills = assessment.selected_skills or ""

    skills_list = [
        skill.strip().lower()
        for skill in selected_skills.split(',')
        if skill.strip()
    ]

    # Student preferences
    career_interest = (
        assessment.career_interest or ""
    ).strip().lower()

    enjoyed_field = (
        assessment.enjoyed_field or ""
    ).strip().lower()

    # Career information
    career_data = [

        {
            'title': 'Full Stack Developer',

            'skills': [
                'HTML/CSS',
                'JavaScript',
                'React',
                'Python',
                'Django',
                'SQL'
            ],

            'description':
                'Build complete web applications using frontend and backend technologies.',

            'required_skills':
                'HTML/CSS, JavaScript, React, Python, Django, SQL'
        },

        {
            'title': 'Java Developer',

            'skills': [
                'Java',
                'Spring Boot',
                'SQL',
                'HTML/CSS',
                'JavaScript'
            ],

            'description':
                'Develop enterprise applications and backend systems using Java technologies.',

            'required_skills':
                'Java, Spring Boot, SQL, HTML/CSS, JavaScript'
        },

        {
            'title': 'Data Analyst',

            'skills': [
                'Python',
                'SQL',
                'Excel',
                'Pandas',
                'Statistics'
            ],

            'description':
                'Analyze data and generate useful business insights using analytics tools.',

            'required_skills':
                'Python, SQL, Excel, Pandas, Statistics'
        },

        {
            'title': 'AI Engineer',

            'skills': [
                'Python',
                'SQL',
                'Pandas',
                'Machine Learning'
            ],

            'description':
                'Build intelligent systems using machine learning and artificial intelligence.',

            'required_skills':
                'Python, SQL, Pandas, Machine Learning'
        },

        {
            'title': 'Cyber Security',

            'skills': [
                'Python',
                'Linux',
                'SQL',
                'Networking'
            ],

            'description':
                'Protect systems, networks and applications from cyber security threats.',

            'required_skills':
                'Python, Linux, SQL, Networking'
        }
    ]

    recommendations = []

    # Calculate personalized recommendation
    for career in career_data:

        required_skills_lower = [
            skill.lower()
            for skill in career['skills']
        ]

        # Matched skills
        matched_skills = [
            career['skills'][i]
            for i, skill in enumerate(required_skills_lower)
            if skill in skills_list
        ]

        # Missing skills
        missing_skills = [
            career['skills'][i]
            for i, skill in enumerate(required_skills_lower)
            if skill not in skills_list
        ]

        # Skill match percentage
        if required_skills_lower:

            skill_match = (
                len(matched_skills)
                / len(required_skills_lower)
            ) * 100

        else:

            skill_match = 0

        # Preference bonus
        preference_bonus = 0

        career_name = career['title'].lower()

        # Career interest match
        if career_interest:

            if (
                career_name in career_interest
                or career_interest in career_name
            ):
                preference_bonus += 20

        # Enjoyed field bonus
        if enjoyed_field:

            if (
                career['title'] == 'Full Stack Developer'
                and 'building applications' in enjoyed_field
            ):
                preference_bonus += 10

            elif (
                career['title'] == 'Data Analyst'
                and 'analyzing data' in enjoyed_field
            ):
                preference_bonus += 10

            elif (
                career['title'] == 'AI Engineer'
                and 'artificial intelligence' in enjoyed_field
            ):
                preference_bonus += 10

            elif (
                career['title'] == 'Cyber Security'
                and 'cyber security' in enjoyed_field
            ):
                preference_bonus += 10

        # Final match score
        final_match = round(
            min(
                skill_match + preference_bonus,
                100
            )
        )

        recommendations.append({

            'title': career['title'],

            # For templates using career.name
            'name': career['title'],

            'match': final_match,

            'description': career['description'],

            'required_skills': career['required_skills'],

            'matched_skills': matched_skills,

            'missing_skills': missing_skills,

            # IMPORTANT:
            # Used by career-recommendation.html
            'skills': career['skills']
        })

    # Highest match first
    recommendations.sort(
        key=lambda x: x['match'],
        reverse=True
    )

    # =====================================================
    # TOP RECOMMENDED CAREER
    # =====================================================

    if recommendations:

        top_recommendation = recommendations[0]

        career = top_recommendation['title']

        career_info = top_recommendation

        # IMPORTANT FIX:
        # Save recommended career for Learning Path
        assessment.recommended_career = career

        assessment.save(
            update_fields=['recommended_career']
        )

    else:

        career = ''

        career_info = {}

    # =====================================================
    # SEND DATA TO TEMPLATE
    # =====================================================

    return render(
        request,
        'career-recommendation.html',
        {
            'assessment': assessment,

            'recommendations': recommendations,

            'selected_skills': selected_skills,

            'career_interest':
                assessment.career_interest,

            'enjoyed_field':
                assessment.enjoyed_field,

            'career': career,

            'career_info': career_info
        }
    )


# =========================================================
# RECOMMEND CAREER
# =========================================================

@login_required
def recommend_career(request):

    if request.method != "POST":
        return redirect(
            "career_recommendation"
        )

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        return redirect(
            "skill_assessment"
        )

    skills_text = (
        assessment.selected_skills or ""
    ).lower()

    skills = [
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    ]

    career_interest = (
        assessment.career_interest or ""
    ).lower()

    career_scores = {
        "Java Developer": [
            "java",
            "sql",
            "spring boot",
            "git",
        ],

        "Python Developer": [
            "python",
            "django",
            "sql",
            "git",
        ],

        "Data Analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "data analysis",
            "statistics",
        ],

        "Business Analyst": [
            "business analysis",
            "excel",
            "sql",
            "power bi",
            "communication",
            "data analysis",
        ],

        "AI/ML Engineer": [
            "python",
            "machine learning",
            "deep learning",
            "statistics",
            "sql",
        ],

        "Full Stack Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "django",
            "sql",
        ],

        "Cyber Security Analyst": [
            "cyber security",
            "networking",
            "linux",
            "python",
            "security",
        ],
    }

    best_career = "Business Analyst"
    best_score = 0

    for career, required_skills in career_scores.items():

        matched = 0

        for required in required_skills:

            if required.lower() in skills:
                matched += 1

        score = round(
            matched /
            len(required_skills) * 100
        )

        if career_interest in career.lower():
            score += 10

        score = min(score, 100)

        if score > best_score:

            best_score = score
            best_career = career

    assessment.recommended_career = best_career
    assessment.save()

    return redirect(
        "career_recommendation"
    )


# =========================================================
# LEARNING PATH
# =========================================================

@login_required(login_url='login')
def learning_path(request):

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )

    except UserSkillAssessment.DoesNotExist:

        return redirect('skill_assessment')

    # -----------------------------------------------------
    # Get career from URL first
    # -----------------------------------------------------

    selected_career = request.GET.get(
        'career',
        ''
    ).strip()

    # -----------------------------------------------------
    # If URL has career, use it
    # -----------------------------------------------------

    if selected_career:

        target_career = selected_career

        # Save it for future use
        assessment.recommended_career = target_career

        assessment.save(
            update_fields=['recommended_career']
        )

    else:

        # Otherwise use saved recommended career
        target_career = (
            assessment.recommended_career or ''
        ).strip()

    # -----------------------------------------------------
    # If still empty, use career interest
    # -----------------------------------------------------

    if not target_career:

        target_career = (
            assessment.career_interest or ''
        ).strip()

    # -----------------------------------------------------
    # Learning paths
    # -----------------------------------------------------

    learning_paths = {

        'Full Stack Developer': {

            'duration': '4–6 Months',

            'steps': [

                {
                    'title':
                        'HTML, CSS & JavaScript',

                    'description':
                        'Strengthen frontend development fundamentals.',

                    'skills': [
                        'HTML',
                        'CSS',
                        'JavaScript',
                        'Responsive Design'
                    ]
                },

                {
                    'title':
                        'React',

                    'description':
                        'Learn modern frontend development using React.',

                    'skills': [
                        'Components',
                        'Hooks',
                        'State Management',
                        'Routing'
                    ]
                },

                {
                    'title':
                        'Python & Django',

                    'description':
                        'Build backend applications using Django.',

                    'skills': [
                        'Python',
                        'Django',
                        'REST API',
                        'Authentication'
                    ]
                },

                {
                    'title':
                        'SQL & Database',

                    'description':
                        'Learn database concepts required for full stack development.',

                    'skills': [
                        'MySQL',
                        'SQL Queries',
                        'Joins',
                        'Database Design'
                    ]
                },

                {
                    'title':
                        'Full Stack Project',

                    'description':
                        'Build a complete real-world web application.',

                    'skills': [
                        'Frontend',
                        'Backend',
                        'Database',
                        'Deployment'
                    ]
                },

                {
                    'title':
                        'Interview Preparation',

                    'description':
                        'Prepare for technical and HR interviews.',

                    'skills': [
                        'Coding',
                        'SQL Questions',
                        'Projects',
                        'HR Interview'
                    ]
                }
            ]
        },

        'Java Developer': {

            'duration': '4–6 Months',

            'steps': [

                {
                    'title':
                        'Java Fundamentals',

                    'description':
                        'Strengthen your core Java programming concepts.',

                    'skills': [
                        'Java',
                        'OOP',
                        'Collections',
                        'Exception Handling'
                    ]
                },

                {
                    'title':
                        'SQL & Database',

                    'description':
                        'Learn database concepts required for backend development.',

                    'skills': [
                        'MySQL',
                        'SQL Queries',
                        'Joins',
                        'Database Design'
                    ]
                },

                {
                    'title':
                        'Spring Boot',

                    'description':
                        'Build modern Java backend applications.',

                    'skills': [
                        'Spring Boot',
                        'REST API',
                        'JPA',
                        'Hibernate'
                    ]
                },

                {
                    'title':
                        'Java Backend Project',

                    'description':
                        'Build a real-world Java backend application.',

                    'skills': [
                        'Java',
                        'Spring Boot',
                        'MySQL',
                        'REST API'
                    ]
                },

                {
                    'title':
                        'Interview Preparation',

                    'description':
                        'Prepare for Java technical interviews.',

                    'skills': [
                        'Java Questions',
                        'SQL',
                        'Coding',
                        'HR Interview'
                    ]
                }
            ]
        },

        'Data Analyst': {

            'duration': '3–5 Months',

            'steps': [

                {
                    'title':
                        'Excel Fundamentals',

                    'description':
                        'Learn spreadsheet-based data analysis.',

                    'skills': [
                        'Excel',
                        'Formulas',
                        'Pivot Tables',
                        'Charts'
                    ]
                },

                {
                    'title':
                        'SQL & Database',

                    'description':
                        'Learn how to query and analyze databases.',

                    'skills': [
                        'SQL',
                        'Joins',
                        'Subqueries',
                        'Database'
                    ]
                },

                {
                    'title':
                        'Python for Data Analysis',

                    'description':
                        'Use Python to clean and analyze datasets.',

                    'skills': [
                        'Python',
                        'Pandas',
                        'NumPy',
                        'Data Cleaning'
                    ]
                },

                {
                    'title':
                        'Data Visualization',

                    'description':
                        'Create dashboards and communicate insights.',

                    'skills': [
                        'Power BI',
                        'Tableau',
                        'Charts',
                        'Dashboards'
                    ]
                },

                {
                    'title':
                        'Data Analytics Project',

                    'description':
                        'Build a real-world data analysis project.',

                    'skills': [
                        'Data Cleaning',
                        'Analysis',
                        'Visualization',
                        'Insights'
                    ]
                },

                {
                    'title':
                        'Interview Preparation',

                    'description':
                        'Prepare for data analyst interviews.',

                    'skills': [
                        'SQL Questions',
                        'Statistics',
                        'Case Studies',
                        'HR Interview'
                    ]
                }
            ]
        },

        'AI Engineer': {

            'duration': '5–7 Months',

            'steps': [

                {
                    'title':
                        'Python Programming',

                    'description':
                        'Build strong Python programming fundamentals.',

                    'skills': [
                        'Python',
                        'OOP',
                        'Functions',
                        'Data Structures'
                    ]
                },

                {
                    'title':
                        'Mathematics & Statistics',

                    'description':
                        'Learn mathematical concepts used in machine learning.',

                    'skills': [
                        'Statistics',
                        'Probability',
                        'Linear Algebra'
                    ]
                },

                {
                    'title':
                        'Machine Learning',

                    'description':
                        'Learn machine learning algorithms and workflows.',

                    'skills': [
                        'Scikit-learn',
                        'Regression',
                        'Classification',
                        'Clustering'
                    ]
                },

                {
                    'title':
                        'Deep Learning',

                    'description':
                        'Build neural network based AI applications.',

                    'skills': [
                        'Neural Networks',
                        'TensorFlow',
                        'PyTorch',
                        'Deep Learning'
                    ]
                },

                {
                    'title':
                        'AI Project',

                    'description':
                        'Build and deploy an AI-powered application.',

                    'skills': [
                        'Model Training',
                        'API',
                        'Deployment',
                        'MLOps'
                    ]
                },

                {
                    'title':
                        'AI Interview Preparation',

                    'description':
                        'Prepare for AI and machine learning interviews.',

                    'skills': [
                        'ML Questions',
                        'Python',
                        'Coding',
                        'HR Interview'
                    ]
                }
            ]
        },

        'Cyber Security': {

            'duration': '4–6 Months',

            'steps': [

                {
                    'title':
                        'Networking Fundamentals',

                    'description':
                        'Learn networking concepts required for cyber security.',

                    'skills': [
                        'TCP/IP',
                        'DNS',
                        'HTTP',
                        'Networking'
                    ]
                },

                {
                    'title':
                        'Linux Fundamentals',

                    'description':
                        'Learn Linux administration and command line tools.',

                    'skills': [
                        'Linux',
                        'Terminal',
                        'File System',
                        'Permissions'
                    ]
                },

                {
                    'title':
                        'Cyber Security Fundamentals',

                    'description':
                        'Understand common security threats and protection methods.',

                    'skills': [
                        'Threats',
                        'Vulnerabilities',
                        'Encryption',
                        'Security'
                    ]
                },

                {
                    'title':
                        'Ethical Hacking',

                    'description':
                        'Learn ethical hacking and security testing concepts.',

                    'skills': [
                        'Penetration Testing',
                        'OWASP',
                        'Security Tools',
                        'Web Security'
                    ]
                },

                {
                    'title':
                        'Cyber Security Project',

                    'description':
                        'Build a practical security project.',

                    'skills': [
                        'Security Testing',
                        'Network Security',
                        'Monitoring',
                        'Reporting'
                    ]
                },

                {
                    'title':
                        'Security Interview Preparation',

                    'description':
                        'Prepare for cyber security interviews.',

                    'skills': [
                        'Security Questions',
                        'Networking',
                        'Linux',
                        'HR Interview'
                    ]
                }
            ]
        }
    }

    # -----------------------------------------------------
    # Match career
    # -----------------------------------------------------

    career_path = learning_paths.get(
        target_career
    )

    # -----------------------------------------------------
    # If career is not in learning paths
    # -----------------------------------------------------

    if career_path is None:

        # Try case-insensitive matching
        matched_career = None

        for career_name in learning_paths:

            if career_name.lower() == target_career.lower():

                matched_career = career_name

                break

        if matched_career:

            target_career = matched_career

            career_path = learning_paths[
                matched_career
            ]

        else:

            # Final fallback
            target_career = 'Full Stack Developer'

            career_path = learning_paths[
                'Full Stack Developer'
            ]

    # -----------------------------------------------------
    # Roadmap
    # -----------------------------------------------------

    roadmap = career_path['steps']

    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render(
        request,
        'learning-path.html',
        {
            'assessment':
                assessment,

            'target_career':
                target_career,

            'duration':
                career_path['duration'],

            'roadmap':
                roadmap
        }
    )


@login_required(login_url='login')
def complete_learning_step(request):

    if request.method == 'POST':

        step_number = int(
            request.POST.get('step_number', 0)
        )

        total_steps = int(
            request.POST.get('total_steps', 0)
        )

        assessment, created = UserSkillAssessment.objects.get_or_create(
            user=request.user
        )

        if total_steps > 0 and step_number > 0:

            completed_steps = assessment.learning_progress

            step_progress = round(
                100 / total_steps
            )

            new_progress = min(
                completed_steps + step_progress,
                100
            )

            assessment.learning_progress = new_progress

            assessment.save(
                update_fields=['learning_progress']
            )

        return redirect('learning_path')

    return redirect('learning_path')


# =========================================================
# RESUME ANALYZER
# =========================================================

@login_required
def resume_view(request):

    resume = None
    analysis = None
    error = None

    try:
        resume = Resume.objects.get(
            user=request.user
        )
    except Resume.DoesNotExist:
        resume = None

    # -----------------------------------------
    # POST - Upload & Analyze
    # -----------------------------------------

    if request.method == "POST":

        uploaded_file = request.FILES.get(
            "resume"
        )

        if not uploaded_file:

            error = (
                "Please select a PDF or DOCX resume."
            )

        else:

            file_name = uploaded_file.name.lower()

            # File validation
            if not (
                file_name.endswith(".pdf")
                or file_name.endswith(".docx")
            ):

                error = (
                    "Only PDF and DOCX files are supported."
                )

            else:

                try:

                    # --------------------------------
                    # Extract Resume Text
                    # --------------------------------

                    resume_text = ""

                    if file_name.endswith(".pdf"):

                        from pypdf import PdfReader

                        reader = PdfReader(
                            uploaded_file
                        )

                        for page in reader.pages:

                            text = page.extract_text()

                            if text:
                                resume_text += (
                                    text + "\n"
                                )

                    elif file_name.endswith(".docx"):

                        from docx import Document

                        document = Document(
                            uploaded_file
                        )

                        for paragraph in document.paragraphs:

                            if paragraph.text.strip():

                                resume_text += (
                                    paragraph.text
                                    + "\n"
                                )

                    resume_text = resume_text.strip()

                    # --------------------------------
                    # Empty Resume
                    # --------------------------------

                    if not resume_text:

                        error = (
                            "Could not extract text from "
                            "this resume. Please upload a "
                            "text-based PDF or DOCX file."
                        )

                    else:

                        # --------------------------------
                        # Skills
                        # --------------------------------

                        RESUME_SKILLS = [

                            "python",
                            "java",
                            "javascript",
                            "html",
                            "css",
                            "react",
                            "django",
                            "spring boot",
                            "sql",
                            "mysql",
                            "postgresql",
                            "mongodb",

                            "excel",
                            "power bi",
                            "tableau",

                            "data analysis",
                            "statistics",

                            "machine learning",
                            "deep learning",
                            "artificial intelligence",
                            "ai",

                            "cyber security",
                            "networking",
                            "linux",

                            "git",
                            "github",
                            "rest api",

                            "communication",
                            "leadership",
                            "business analysis",
                            "problem solving",
                        ]

                        text_lower = (
                            resume_text.lower()
                        )

                        detected_skills = []

                        for skill in RESUME_SKILLS:

                            if skill.lower() in text_lower:

                                detected_skills.append(
                                    skill
                                )

                        # --------------------------------
                        # Word Count
                        # --------------------------------

                        word_count = len(
                            resume_text.split()
                        )

                        # --------------------------------
                        # ATS SCORE
                        # --------------------------------

                        score = 0

                        # Resume length
                        if word_count >= 300:

                            score += 20

                        elif word_count >= 150:

                            score += 15

                        elif word_count >= 75:

                            score += 10

                        else:

                            score += 5

                        # Skills
                        if len(detected_skills) >= 8:

                            score += 25

                        elif len(detected_skills) >= 5:

                            score += 20

                        elif len(detected_skills) >= 3:

                            score += 15

                        elif len(detected_skills) >= 1:

                            score += 10

                        # --------------------------------
                        # Resume Sections
                        # --------------------------------

                        sections = {

                            "education": [
                                "education",
                                "academic",
                                "qualification",
                            ],

                            "experience": [
                                "experience",
                                "work experience",
                                "employment",
                            ],

                            "skills": [
                                "skills",
                                "technical skills",
                                "skill set",
                            ],

                            "projects": [
                                "projects",
                                "project",
                            ],

                            "certifications": [
                                "certification",
                                "certifications",
                                "certificate",
                            ],
                        }

                        found_sections = 0

                        for section_words in sections.values():

                            if any(
                                word in text_lower
                                for word in section_words
                            ):

                                found_sections += 1

                        if found_sections >= 5:

                            score += 25

                        elif found_sections >= 4:

                            score += 20

                        elif found_sections >= 3:

                            score += 15

                        elif found_sections >= 2:

                            score += 10

                        else:

                            score += 5

                        # --------------------------------
                        # Contact Information
                        # --------------------------------

                        contact_score = 0

                        if "@" in resume_text:

                            contact_score += 5

                        phone_text = (
                            resume_text
                            .replace(" ", "")
                            .replace("-", "")
                        )

                        if re.search(
                            r"\b\d{10}\b",
                            phone_text
                        ):

                            contact_score += 5

                        score += contact_score

                        # --------------------------------
                        # Action Words
                        # --------------------------------

                        action_words = [

                            "developed",
                            "created",
                            "implemented",
                            "managed",
                            "designed",
                            "analyzed",
                            "improved",
                            "led",
                            "built",
                            "achieved",
                        ]

                        action_count = sum(
                            1
                            for word in action_words
                            if word in text_lower
                        )

                        if action_count >= 4:

                            score += 10

                        elif action_count >= 2:

                            score += 7

                        elif action_count >= 1:

                            score += 4

                        # Maximum 100
                        score = min(
                            score,
                            100
                        )

                        # --------------------------------
                        # Suggestions
                        # --------------------------------

                        suggestions = []

                        if word_count < 150:

                            suggestions.append(
                                "Add more relevant details "
                                "to your resume."
                            )

                        if len(detected_skills) < 5:

                            suggestions.append(
                                "Add more relevant technical "
                                "and professional skills."
                            )

                        if found_sections < 4:

                            suggestions.append(
                                "Include important sections "
                                "such as Education, Experience, "
                                "Skills and Projects."
                            )

                        if "@" not in resume_text:

                            suggestions.append(
                                "Add a professional email address."
                            )

                        if action_count < 2:

                            suggestions.append(
                                "Use strong action words such as "
                                "Developed, Implemented, Designed "
                                "and Managed."
                            )

                        if score >= 80:

                            suggestions.append(
                                "Your resume has good ATS "
                                "compatibility. Continue "
                                "tailoring it to each job description."
                            )

                        elif score >= 60:

                            suggestions.append(
                                "Your resume is reasonably "
                                "ATS-friendly. Improve missing "
                                "sections and keywords."
                            )

                        else:

                            suggestions.append(
                                "Improve your resume structure, "
                                "skills and job-related keywords "
                                "to increase ATS compatibility."
                            )

                        # --------------------------------
                        # SAVE RESUME
                        # --------------------------------

                        if resume:

                            resume.resume_file = (
                                uploaded_file
                            )

                        else:

                            resume = Resume(
                                user=request.user,
                                resume_file=uploaded_file
                            )

                        resume.ats_score = score

                        resume.detected_skills = (
                            ", ".join(
                                detected_skills
                            )
                        )

                        resume.save()

                        # --------------------------------
                        # Analysis
                        # --------------------------------

                        analysis = {

                            "ats_score": score,

                            "detected_skills":
                                detected_skills,

                            "word_count":
                                word_count,

                            "sections_found":
                                found_sections,

                            "action_words":
                                action_count,

                            "suggestions":
                                suggestions,
                        }

                except Exception as e:

                    error = (
                        f"Resume analysis failed: {str(e)}"
                    )

    # -----------------------------------------
    # Existing Resume
    # -----------------------------------------

    if resume and not analysis:

        existing_skills = []

        if resume.detected_skills:

            existing_skills = [

                skill.strip()

                for skill
                in resume.detected_skills.split(",")

                if skill.strip()
            ]

        analysis = {

            "ats_score":
                resume.ats_score,

            "detected_skills":
                existing_skills,

            "word_count":
                None,

            "sections_found":
                None,

            "action_words":
                None,

            "suggestions": [

                "Upload a new resume to perform "
                "a fresh analysis."

            ],
        }

    return render(
        request,
        "resume.html",
        {
            "resume": resume,
            "analysis": analysis,
            "error": error,
        }
    )


# =========================================================
# MOCK INTERVIEW QUESTIONS
# =========================================================

INTERVIEW_QUESTIONS = {

    "Java Developer": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Java development.",
            "Can you explain what Java is and where you have used it?",
            "What are classes and objects in Java? Can you give a simple example?",
            "Suppose you are developing a small application. Why would you choose Java for it?",
            "Tell me about a Java project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Can you walk me through a Java project you have worked on and explain your contribution?",
            "How would you decide between using ArrayList and LinkedList in a real application?",
            "Tell me about a situation where you used exception handling in a project.",
            "If a Java application becomes slow, how would you investigate the problem?",
            "How have you used Spring Boot or how would you use it to build a REST API?"
        ],

        "Advanced": [
            "Imagine a Java application is handling thousands of requests and response time is increasing. How would you troubleshoot it?",
            "How would you design a scalable Spring Boot REST API for a production application?",
            "What techniques would you use to improve Java application performance?",
            "How would you handle concurrency when multiple users update the same data?",
            "Tell me about a challenging Java problem you solved and how you approached it."
        ],
    },


    "Python Developer": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Python development.",
            "What is Python and why is it popular in software development?",
            "Can you explain the difference between a list and a tuple with an example?",
            "Suppose you need to store multiple student names. Which Python data structure would you choose and why?",
            "Tell me about a Python project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Can you walk me through a Python project you have worked on and explain your contribution?",
            "How do you handle exceptions in a Python application?",
            "What are decorators in Python and where might you use them?",
            "If a Python application is running slowly, how would you identify the bottleneck?",
            "How would you use Django to build a backend application?"
        ],

        "Advanced": [
            "Imagine your Python application needs to process a very large dataset. How would you improve its performance?",
            "How would you design a scalable Python backend for a production application?",
            "When would you use multiprocessing, multithreading, or asynchronous programming in Python?",
            "How would you identify and fix a memory-related performance issue in Python?",
            "Tell me about a difficult Python problem you solved and explain your approach."
        ],
    },


    "Data Analyst": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Data Analytics.",
            "What is data analysis and why is it important for a company?",
            "What is the difference between a row and a column in a dataset?",
            "Suppose a dataset contains missing values. What would you do?",
            "Tell me about a data analysis project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Walk me through a data analysis project you have worked on. What was your approach?",
            "How would you use SQL to find useful information from a large dataset?",
            "Can you explain the difference between INNER JOIN and LEFT JOIN with a practical example?",
            "A business manager says sales have dropped this month. How would you investigate the reason using data?",
            "How would you present your analysis and recommendations to a non-technical manager?"
        ],

        "Advanced": [
            "Suppose sales decreased by 20% this quarter. How would you identify the root cause using data?",
            "How would you optimize a complex SQL query running on a large database?",
            "How would you design a dashboard for senior management to track business performance?",
            "How would you determine whether an observed business trend is actually meaningful?",
            "Tell me about a challenging data problem you solved and how your analysis influenced the decision."
        ],
    },


    "Business Analyst": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Business Analysis.",
            "What does a Business Analyst do in an IT company?",
            "What is requirements gathering?",
            "Suppose a client is not clear about what they need. How would you understand their requirement?",
            "Tell me about a project where you worked with different people or teams."
        ],

        "Intermediate": [
            "Walk me through a project where you gathered and documented requirements.",
            "How would you handle two stakeholders who have conflicting requirements?",
            "Can you explain the difference between functional and non-functional requirements with an example?",
            "A client changes an important requirement just before development. How would you handle it?",
            "How would you use data to identify the root cause of a business problem?"
        ],

        "Advanced": [
            "A business team reports that a new system is not improving productivity. How would you investigate the problem?",
            "How would you prioritize requirements when different stakeholders consider everything important?",
            "How would you measure whether an IT solution has actually delivered business value?",
            "Imagine the development team says a requirement is technically difficult and expensive. How would you handle the discussion with the stakeholders?",
            "Tell me about a difficult stakeholder or business problem you handled and how you reached a solution."
        ],
    },


    "AI Engineer": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in AI Engineering.",
            "What is Artificial Intelligence and where do we use it in real life?",
            "Can you explain Machine Learning in simple terms?",
            "What is the difference between AI and Machine Learning?",
            "Tell me about an AI or Machine Learning project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Walk me through a Machine Learning project you have worked on and explain your contribution.",
            "What is the difference between supervised and unsupervised learning?",
            "Suppose your model performs very well on training data but poorly on test data. What could be the reason?",
            "How would you handle missing or incorrect data before training a Machine Learning model?",
            "How would you explain the result of your AI model to a non-technical manager?"
        ],

        "Advanced": [
            "Imagine your Machine Learning model performs well in testing but poorly after deployment. How would you investigate the problem?",
            "How would you design an AI system that needs to process a large amount of data in production?",
            "How would you decide which Machine Learning algorithm is appropriate for a new business problem?",
            "How would you monitor a Machine Learning model after deployment?",
            "Tell me about a challenging AI problem you solved and explain the decisions you made."
        ],
    },


    "Full Stack Developer": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Full Stack Development.",
            "Can you explain the role of HTML, CSS and JavaScript in a web application?",
            "What is the difference between frontend and backend development?",
            "Suppose you need to create a simple login page. What technologies would you use?",
            "Tell me about a web project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Walk me through a full stack project you have worked on and explain your contribution.",
            "How does a REST API allow the frontend and backend to communicate?",
            "How would you design a login and registration system for a web application?",
            "If a web application is loading slowly, how would you identify and fix the problem?",
            "How have you used a database in your web application?"
        ],

        "Advanced": [
            "Imagine your web application suddenly receives ten times more users. How would you make the system scalable?",
            "How would you design a secure authentication system for a production web application?",
            "How would you improve the performance of a full stack application?",
            "How would you handle failures between frontend, backend and database services?",
            "Tell me about a challenging full stack problem you solved and how you approached it."
        ],
    },


    "Cyber Security Analyst": {

        "Beginner": [
            "Hi, please introduce yourself and tell me why you are interested in Cyber Security.",
            "What is Cyber Security and why is it important for an organization?",
            "What is a firewall and what does it do?",
            "Can you explain phishing with a real-world example?",
            "Tell me about a security project you have worked on or would like to build."
        ],

        "Intermediate": [
            "Walk me through a security-related project you have worked on.",
            "A user reports receiving a suspicious email. How would you investigate it?",
            "What is the difference between authentication and authorization?",
            "How would you identify a possible security incident in an organization's network?",
            "What steps would you take after discovering a compromised user account?"
        ],

        "Advanced": [
            "Imagine multiple systems in an organization show unusual activity. How would you approach the incident investigation?",
            "How would you design a security monitoring strategy for a medium-sized organization?",
            "How would you prioritize vulnerabilities when an organization has hundreds of security findings?",
            "How would you respond if sensitive company data was suspected to have been exposed?",
            "Tell me about a challenging security problem you solved and explain your approach."
        ],
    },


    "General": {

        "Beginner": [
            "Hi, please introduce yourself.",
            "What are your strongest technical skills?",
            "Why did you choose your current career direction?",
            "Tell me about a project you have worked on.",
            "What are you currently learning?"
        ],

        "Intermediate": [
            "Please introduce yourself and walk me through your technical background.",
            "Tell me about a project where you faced a technical challenge.",
            "How do you approach learning a new technology?",
            "Tell me about a time when you worked with a team to solve a problem.",
            "Where do you see yourself professionally in the next few years?"
        ],

        "Advanced": [
            "Tell me about the most challenging technical problem you have solved.",
            "How do you make technical decisions when there are multiple possible solutions?",
            "Describe a situation where your technical decision had a significant impact on a project.",
            "How would you approach designing a solution for an unfamiliar business problem?",
            "Why should an IT company hire you for this role?"
        ],
    },
}


# =========================================================
# INTERVIEW EVALUATOR
# =========================================================

def evaluate_interview_answer(
    question,
    answer,
    career
):

    answer = answer.strip()

    if not answer:

        return {
            "technical_score": 0,
            "relevance_score": 0,
            "communication_score": 0,
            "overall_score": 0,
            "strengths": [
                "No answer was provided."
            ],
            "improvements": [
                "Provide a clear and complete answer."
            ],
            "feedback": (
                "Please provide an answer "
                "to receive a meaningful evaluation."
            ),
        }

    answer_lower = answer.lower()

    # --------------------------------
    # Technical score
    # --------------------------------

    technical_keywords = {

        "Java Developer": [
            "java",
            "class",
            "object",
            "inheritance",
            "polymorphism",
            "encapsulation",
            "exception",
            "spring",
        ],

        "Python Developer": [
            "python",
            "list",
            "tuple",
            "function",
            "decorator",
            "django",
            "class",
            "object",
        ],

        "Data Analyst": [
            "data",
            "sql",
            "excel",
            "power bi",
            "analysis",
            "statistics",
            "query",
        ],

        "Business Analyst": [
            "business",
            "requirement",
            "stakeholder",
            "analysis",
            "data",
            "process",
            "solution",
        ],

        "AI Engineer": [
            "machine learning",
            "model",
            "training",
            "data",
            "algorithm",
            "supervised",
            "unsupervised",
            "deep learning",
        ],

        "Full Stack Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "django",
            "api",
            "frontend",
            "backend",
        ],

        "Cyber Security Analyst": [
            "security",
            "network",
            "firewall",
            "attack",
            "authentication",
            "authorization",
            "phishing",
            "threat",
        ],

        "General": [
            "experience",
            "skill",
            "team",
            "goal",
            "learning",
            "communication",
        ],
    }

    keywords = technical_keywords.get(
        career,
        technical_keywords["General"]
    )

    matched_keywords = sum(
        1
        for keyword in keywords
        if keyword in answer_lower
    )

    technical_score = min(
        100,
        matched_keywords * 15
    )

    # --------------------------------
    # Relevance
    # --------------------------------

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            question.lower()
        )
    )

    answer_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            answer_lower
        )
    )

    common_words = (
        question_words & answer_words
    )

    relevance_score = min(
        100,
        40 + len(common_words) * 10
    )

    # --------------------------------
    # Communication
    # --------------------------------

    word_count = len(
        answer.split()
    )

    communication_score = 0

    if word_count >= 80:
        communication_score = 95

    elif word_count >= 50:
        communication_score = 85

    elif word_count >= 30:
        communication_score = 75

    elif word_count >= 15:
        communication_score = 60

    else:
        communication_score = 40

    # --------------------------------
    # Overall
    # --------------------------------

    overall_score = round(

        technical_score * 0.40

        + relevance_score * 0.30

        + communication_score * 0.30
    )

    # --------------------------------
    # Strengths
    # --------------------------------

    strengths = []

    if word_count >= 30:

        strengths.append(
            "Good answer length and explanation."
        )

    if matched_keywords >= 3:

        strengths.append(
            "Good use of relevant technical keywords."
        )

    if relevance_score >= 70:

        strengths.append(
            "Answer is relevant to the question."
        )

    if not strengths:

        strengths.append(
            "You attempted to answer the question."
        )

    # --------------------------------
    # Improvements
    # --------------------------------

    improvements = []

    if technical_score < 60:

        improvements.append(
            "Include more technical concepts "
            "related to the question."
        )

    if relevance_score < 70:

        improvements.append(
            "Keep your answer more closely "
            "related to the question."
        )

    if communication_score < 70:

        improvements.append(
            "Give a more detailed and structured answer."
        )

    if not improvements:

        improvements.append(
            "Continue using examples to strengthen your answer."
        )

    feedback = (
        f"Your overall score is {overall_score}/100. "
        f"Technical: {technical_score}/100, "
        f"Relevance: {relevance_score}/100, "
        f"Communication: {communication_score}/100."
    )

    return {

        "technical_score":
            technical_score,

        "relevance_score":
            relevance_score,

        "communication_score":
            communication_score,

        "overall_score":
            overall_score,

        "strengths":
            strengths,

        "improvements":
            improvements,

        "feedback":
            feedback,
    }


# =========================================================
# MOCK INTERVIEW
# =========================================================

@login_required
def mock_interview(request):

    # --------------------------------
    # Get career from URL
    # --------------------------------

    career = request.GET.get("career", "").strip()

    # --------------------------------
    # Get assessment
    # --------------------------------

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        assessment = None

    # --------------------------------
    # If career is not provided,
    # get it from user's assessment
    # --------------------------------

    if not career and assessment:

        career = (
            assessment.recommended_career
            or assessment.career_interest
            or ""
        ).strip()

    # --------------------------------
    # Session fallback
    # --------------------------------

    if not career:

        career = request.session.get(
            "interview_career",
            ""
        ).strip()

    # --------------------------------
    # Final fallback
    # --------------------------------

    if not career:
        career = "General"

    # --------------------------------
    # Career aliases
    # --------------------------------

    career_aliases = {

        "Python Developer":
            "Python Developer",

        "AI/ML Engineer":
            "AI Engineer",

        "AI & ML Engineer":
            "AI Engineer",

        "Machine Learning Engineer":
            "AI Engineer",

        "Cybersecurity Analyst":
            "Cyber Security Analyst",

        "Business Analytics":
            "Business Analyst",

        "Data Analytics":
            "Data Analyst",

    }

    career = career_aliases.get(
        career,
        career
    )

    # --------------------------------
    # Get student's skill levels
    # --------------------------------

    skill_levels = {}

    if assessment:

        skill_levels = (
            assessment.skill_levels
            if assessment.skill_levels
            else {}
        )

    # --------------------------------
    # Determine interview level
    # --------------------------------
    #
    # If multiple skills have different
    # levels, use the highest level.
    #
    # Beginner = 1
    # Intermediate = 2
    # Advanced = 3
    # --------------------------------

    level_priority = {

        "Beginner": 1,

        "Intermediate": 2,

        "Advanced": 3,

    }

    interview_level = "Beginner"

    if skill_levels:

        highest_level = 1

        for level in skill_levels.values():

            priority = level_priority.get(
                level,
                1
            )

            if priority > highest_level:

                highest_level = priority

                interview_level = level

    # --------------------------------
    # Start / Reset interview
    # --------------------------------

    if request.method == "GET":

        request.session[
            "interview_career"
        ] = career

        request.session[
            "interview_level"
        ] = interview_level

        request.session[
            "interview_question_index"
        ] = 0

        request.session[
            "interview_scores"
        ] = []

        request.session[
            "interview_completed"
        ] = False

        request.session.modified = True

    else:

        # Keep values during POST

        career = request.session.get(
            "interview_career",
            career
        )

        interview_level = request.session.get(
            "interview_level",
            interview_level
        )

    # --------------------------------
    # Get career questions
    # --------------------------------

    career_questions = INTERVIEW_QUESTIONS.get(
        career
    )

    # --------------------------------
    # If career doesn't exist
    # --------------------------------

    if not career_questions:

        career = "General"

        career_questions = INTERVIEW_QUESTIONS.get(
            "General",
            {}
        )

        request.session[
            "interview_career"
        ] = career

    # --------------------------------
    # Get level-specific questions
    # --------------------------------

    if isinstance(career_questions, dict):

        questions = career_questions.get(
            interview_level
        )

        # Safety fallback

        if not questions:

            questions = career_questions.get(
                "Beginner",
                []
            )

    else:

        # Backward compatibility
        # in case old question format exists

        questions = career_questions

    # --------------------------------
    # Current question index
    # --------------------------------

    question_index = request.session.get(
        "interview_question_index",
        0
    )

    # --------------------------------
    # POST - Submit Answer
    # --------------------------------

    if request.method == "POST":

        answer = request.POST.get(
            "answer",
            ""
        ).strip()

        # --------------------------------
        # Prevent empty answer
        # --------------------------------

        if not answer:

            current_question = questions[
                min(
                    question_index,
                    len(questions) - 1
                )
            ]

            progress = round(
                (
                    question_index
                    / len(questions)
                ) * 100
            )

            return render(
                request,
                "mock_interview.html",
                {
                    "career": career,

                    "level":
                        interview_level,

                    "question":
                        current_question,

                    "question_number":
                        question_index + 1,

                    "total_questions":
                        len(questions),

                    "progress":
                        progress,

                    "error":
                        "Please enter your answer before continuing."
                }
            )

        # --------------------------------
        # Evaluate answer
        # --------------------------------

        if question_index < len(questions):

            question = questions[
                question_index
            ]

            evaluation = evaluate_interview_answer(
                question,
                answer,
                career
            )

            # --------------------------------
            # Save interview result
            # --------------------------------

            MockInterview.objects.create(

                user=request.user,

                career=career,

                question=question,

                answer=answer,

                score=evaluation[
                    "overall_score"
                ],

                feedback=evaluation[
                    "feedback"
                ],

            )

            # --------------------------------
            # Save score in session
            # --------------------------------

            scores = request.session.get(
                "interview_scores",
                []
            )

            scores.append(
                evaluation
            )

            request.session[
                "interview_scores"
            ] = scores

            # --------------------------------
            # Move to next question
            # --------------------------------

            question_index += 1

            request.session[
                "interview_question_index"
            ] = question_index

            request.session.modified = True

            # --------------------------------
            # Interview completed
            # --------------------------------

            if question_index >= len(questions):

                request.session[
                    "interview_completed"
                ] = True

                request.session.modified = True

                return redirect(
                    "interview_result"
                )

    # --------------------------------
    # Safety check
    # --------------------------------

    if not questions:

        return render(
            request,
            "mock_interview.html",
            {
                "career": career,

                "level":
                    interview_level,

                "question":
                    "Tell me about yourself.",

                "question_number": 1,

                "total_questions": 1,

                "progress": 0,
            }
        )

    # --------------------------------
    # Interview completed
    # --------------------------------

    if question_index >= len(questions):

        return redirect(
            "interview_result"
        )

    # --------------------------------
    # Current question
    # --------------------------------

    current_question = questions[
        question_index
    ]

    # --------------------------------
    # Progress
    # --------------------------------

    progress = round(
        (
            question_index
            / len(questions)
        ) * 100
    )

    # --------------------------------
    # Render Interview
    # --------------------------------

    return render(
        request,
        "mock_interview.html",
        {
            "career":
                career,

            "level":
                interview_level,

            "question":
                current_question,

            "question_number":
                question_index + 1,

            "total_questions":
                len(questions),

            "progress":
                progress,
        }
    )


# =========================================================
# INTERVIEW RESULT
# =========================================================

@login_required
def interview_result(request):

    career = request.session.get(
        "interview_career",
        "General"
    )

    # Latest 5 interviews for career
    interviews = MockInterview.objects.filter(
        user=request.user,
        career=career
    ).order_by("-created_at")[:5]

    interviews = list(
        reversed(interviews)
    )

    average_score = 0
    highest_score = 0
    lowest_score = 0

    technical_average = 0
    relevance_average = 0
    communication_average = 0

    detailed_results = []

    if interviews:

        scores = [
            interview.score
            for interview in interviews
        ]

        average_score = round(
            sum(scores) / len(scores)
        )

        highest_score = max(scores)
        lowest_score = min(scores)

        technical_scores = []
        relevance_scores = []
        communication_scores = []

        for interview in interviews:

            evaluation = evaluate_interview_answer(
                interview.question,
                interview.answer,
                career
            )

            technical_scores.append(
                evaluation[
                    "technical_score"
                ]
            )

            relevance_scores.append(
                evaluation[
                    "relevance_score"
                ]
            )

            communication_scores.append(
                evaluation[
                    "communication_score"
                ]
            )

            detailed_results.append({

                "question":
                    interview.question,

                "answer":
                    interview.answer,

                "score":
                    interview.score,

                "technical_score":
                    evaluation[
                        "technical_score"
                    ],

                "relevance_score":
                    evaluation[
                        "relevance_score"
                    ],

                "communication_score":
                    evaluation[
                        "communication_score"
                    ],

                "strengths":
                    evaluation[
                        "strengths"
                    ],

                "improvements":
                    evaluation[
                        "improvements"
                    ],

                "feedback":
                    evaluation[
                        "feedback"
                    ],
            })

        technical_average = round(
            sum(technical_scores)
            / len(technical_scores)
        )

        relevance_average = round(
            sum(relevance_scores)
            / len(relevance_scores)
        )

        communication_average = round(
            sum(communication_scores)
            / len(communication_scores)
        )

    context = {

        "career":
            career,

        "average_score":
            average_score,

        "highest_score":
            highest_score,

        "lowest_score":
            lowest_score,

        "technical_average":
            technical_average,

        "relevance_average":
            relevance_average,

        "communication_average":
            communication_average,

        "detailed_results":
            detailed_results,

        "interviews":
            interviews,
    }

    return render(
        request,
        "interview_result.html",
        context
    )


# =========================================================
# JOB RECOMMENDATION
# =========================================================

@login_required
def job_recommendation(request):

    assessment = None
    resume = None

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        pass

    try:
        resume = Resume.objects.get(
            user=request.user
        )
    except Resume.DoesNotExist:
        pass

    # --------------------------------
    # User skills
    # --------------------------------

    user_skills = set()

    if assessment:

        assessment_skills = (
            assessment.selected_skills
            or ""
        )

        for skill in assessment_skills.split(","):

            skill = skill.strip().lower()

            if skill:
                user_skills.add(skill)

    # Resume skills
    if resume:

        resume_skills = (
            resume.detected_skills
            or ""
        )

        for skill in resume_skills.split(","):

            skill = skill.strip().lower()

            if skill:
                user_skills.add(skill)

    # --------------------------------
    # Static job recommendations
    # --------------------------------

    jobs = [

        {
            "title":
                "Junior Java Developer",

            "company":
                "Software Development Company",

            "location":
                "Chennai",

            "type":
                "Full Time",

            "description":
                "Develop and maintain Java-based applications.",

            "required_skills": [
                "java",
                "sql",
                "spring boot",
                "rest api",
                "git",
            ],
        },

        {
            "title":
                "Full Stack Developer",

            "company":
                "Technology Company",

            "location":
                "Bangalore",

            "type":
                "Full Time",

            "description":
                "Work on frontend and backend web applications.",

            "required_skills": [
                "html",
                "css",
                "javascript",
                "react",
                "django",
                "sql",
                "git",
            ],
        },

        {
            "title":
                "Data Analyst",

            "company":
                "Analytics Company",

            "location":
                "Chennai",

            "type":
                "Full Time",

            "description":
                "Analyze business data and create analytical reports.",

            "required_skills": [
                "python",
                "sql",
                "excel",
                "power bi",
                "data analysis",
                "statistics",
            ],
        },

        {
            "title":
                "Business Analyst",

            "company":
                "Consulting Company",

            "location":
                "Chennai",

            "type":
                "Full Time",

            "description":
                "Analyze business requirements and support decision making.",

            "required_skills": [
                "business analysis",
                "excel",
                "sql",
                "power bi",
                "communication",
                "data analysis",
            ],
        },

        {
            "title":
                "Cyber Security Analyst",

            "company":
                "Cyber Security Company",

            "location":
                "Bangalore",

            "type":
                "Full Time",

            "description":
                "Monitor systems and identify potential security threats.",

            "required_skills": [
                "cyber security",
                "networking",
                "linux",
                "python",
                "security",
            ],
        },

        {
            "title":
                "AI/ML Engineer",

            "company":
                "AI Technology Company",

            "location":
                "Bangalore",

            "type":
                "Full Time",

            "description":
                "Develop machine learning and AI-based solutions.",

            "required_skills": [
                "python",
                "machine learning",
                "deep learning",
                "statistics",
                "sql",
            ],
        },

        {
            "title":
                "Python Developer",

            "company":
                "Technology Company",

            "location":
                "Remote",

            "type":
                "Full Time",

            "description":
                "Develop Python and Django-based web applications.",

            "required_skills": [
                "python",
                "django",
                "sql",
                "rest api",
                "git",
            ],
        },
    ]

    recommendations = []

    career_interest = ""

    if assessment:

        career_interest = (
            assessment.career_interest
            or ""
        ).lower()

    for job in jobs:

        required = job[
            "required_skills"
        ]

        matched_skills = []

        missing_skills = []

        for skill in required:

            if skill.lower() in user_skills:

                matched_skills.append(
                    skill
                )

            else:

                missing_skills.append(
                    skill
                )

        if required:

            match = round(
                len(matched_skills)
                / len(required)
                * 100
            )

        else:

            match = 0

        # Career interest bonus
        if (
            career_interest
            and (
                career_interest
                in job["title"].lower()
                or job["title"].lower()
                in career_interest
            )
        ):

            match += 10

        match = min(
            match,
            100
        )

        job_copy = job.copy()

        job_copy[
            "matched_skills"
        ] = matched_skills

        job_copy[
            "missing_skills"
        ] = missing_skills

        job_copy[
            "match"
        ] = match

        recommendations.append(
            job_copy
        )

    # Highest matches first
    recommendations.sort(
        key=lambda x: x["match"],
        reverse=True
    )

    top_jobs = recommendations[:3]

    return render(
        request,
        "job_recommendation.html",
        {
            "recommendations":
                recommendations,

            "top_jobs":
                top_jobs,

            "user_skills":
                user_skills,

            "assessment":
                assessment,

            "resume":
                resume,
        }
    )


# =========================================================
# SHARE CAREER PROFILE
# =========================================================

@login_required(login_url='login')
def share_career_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name()
        }
    )

    profile.is_profile_shared = True
    profile.save(update_fields=['is_profile_shared'])

    public_path = reverse(
        'public_career_profile',
        kwargs={
            'token': profile.share_token
        }
    )

    if request.get_host().startswith('127.0.0.1') or request.get_host().startswith('localhost'):
        share_url = request.build_absolute_uri(public_path)
    else:
        share_url = f"https://ai-career-coach-1-ftre.onrender.com{public_path}"

    return render(
        request,
        'share-profile.html',
        {
            'share_url': share_url,
            'profile': profile,
        }
    )


# =========================================================
# PUBLIC CAREER PROFILE - INTERVIEWER VIEW
# =========================================================

def public_career_profile(request, token):

    try:
        profile = StudentProfile.objects.get(
            share_token=token,
            is_profile_shared=True
        )
    except StudentProfile.DoesNotExist:
        return render(
            request,
            'profile-not-found.html'
        )

    user = profile.user

    # Skill Assessment
    try:
        assessment = UserSkillAssessment.objects.get(
            user=user
        )
    except UserSkillAssessment.DoesNotExist:
        assessment = None

    # Mock Interview Details
    interviews = MockInterview.objects.filter(
        user=user
    ).order_by('-created_at')

    interview_count = interviews.count()

    if interview_count > 0:
        total_score = sum(
            interview.score for interview in interviews
        )

        average_interview_score = round(
            total_score / interview_count
        )
    else:
        average_interview_score = 0

    context = {
        'profile': profile,
        'assessment': assessment,
        'interviews': interviews,
        'interview_count': interview_count,
        'average_interview_score': average_interview_score,
    }

    return render(
        request,
        'public-career-profile.html',
        context
    )