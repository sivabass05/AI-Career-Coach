from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required

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

@login_required
def skill_assessment(request):

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        assessment = None

    if request.method == "POST":

        selected_skills = request.POST.getlist(
            "selected_skills"
        )

        career_interest = request.POST.get(
            "career_interest",
            ""
        )

        enjoyed_field = request.POST.get(
            "enjoyed_field",
            ""
        )

        # Calculate skill score
        skill_score = min(
            len(selected_skills) * 10,
            100
        )

        if assessment:

            assessment.selected_skills = (
                ", ".join(selected_skills)
            )

            assessment.career_interest = (
                career_interest
            )

            assessment.enjoyed_field = (
                enjoyed_field
            )

            assessment.skill_score = skill_score

            assessment.save()

        else:

            assessment = UserSkillAssessment.objects.create(
                user=request.user,
                selected_skills=", ".join(
                    selected_skills
                ),
                career_interest=career_interest,
                enjoyed_field=enjoyed_field,
                skill_score=skill_score
            )

        return redirect(
            "career_recommendation"
        )

    return render(
        request,
        "skill_assessment.html",
        {
            "assessment": assessment
        }
    )


# =========================================================
# CAREER RECOMMENDATION PAGE
# =========================================================

@login_required
def career_recommendation(request):

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:

        return redirect(
            "skill_assessment"
        )

    return render(
        request,
        "career_recommendation.html",
        {
            "assessment": assessment
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

@login_required
def learning_path(request):

    try:
        assessment = UserSkillAssessment.objects.get(
            user=request.user
        )
    except UserSkillAssessment.DoesNotExist:
        assessment = None

    career = ""

    if assessment:
        career = (
            assessment.recommended_career
            or assessment.career_interest
            or "Business Analyst"
        )

    career_lower = career.lower()

    if "java" in career_lower:

        skills = [
            "Java",
            "OOP",
            "SQL",
            "Spring Boot",
            "REST API",
            "Git",
        ]

        project = (
            "Build a Java Spring Boot Employee "
            "Management System."
        )

    elif "python" in career_lower:

        skills = [
            "Python",
            "OOP",
            "SQL",
            "Django",
            "REST API",
            "Git",
        ]

        project = (
            "Build a Django-based Career "
            "Recommendation System."
        )

    elif "data" in career_lower:

        skills = [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Statistics",
            "Data Analysis",
        ]

        project = (
            "Build a Sales Data Analytics "
            "Dashboard using Python and Power BI."
        )

    elif "business" in career_lower:

        skills = [
            "Business Analysis",
            "Excel",
            "SQL",
            "Power BI",
            "Communication",
            "Data Analysis",
        ]

        project = (
            "Build a Business Performance "
            "Analytics Dashboard."
        )

    elif "ai" in career_lower or "machine" in career_lower:

        skills = [
            "Python",
            "Statistics",
            "Machine Learning",
            "Deep Learning",
            "SQL",
            "Data Processing",
        ]

        project = (
            "Build an AI-based Career "
            "Recommendation Model."
        )

    elif "full stack" in career_lower:

        skills = [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Django",
            "SQL",
            "Git",
        ]

        project = (
            "Build a complete full-stack "
            "student career portal."
        )

    elif "cyber" in career_lower:

        skills = [
            "Networking",
            "Linux",
            "Cyber Security",
            "Python",
            "Security",
            "Ethical Hacking",
        ]

        project = (
            "Build a basic network security "
            "monitoring project."
        )

    else:

        skills = [
            "Communication",
            "Excel",
            "SQL",
            "Data Analysis",
            "Problem Solving",
            "Business Analysis",
        ]

        project = (
            "Build a business analytics "
            "dashboard project."
        )

    return render(
        request,
        "learning_path.html",
        {
            "career": career,
            "skills": skills,
            "project": project,
            "assessment": assessment,
        }
    )


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

    "Java Developer": [

        "What is OOP in Java? Explain its main principles.",

        "What is the difference between ArrayList and LinkedList?",

        "What is exception handling in Java?",

        "What is Spring Boot and why is it used?",

        "Tell me about yourself and why you want to become a Java Developer.",
    ],

    "Python Developer": [

        "What are the main features of Python?",

        "What is the difference between a list and a tuple?",

        "What are decorators in Python?",

        "What is Django and why is it used?",

        "Tell me about yourself and why you want to become a Python Developer.",
    ],

    "Data Analyst": [

        "What is data analysis?",

        "What is the difference between INNER JOIN and LEFT JOIN in SQL?",

        "What is the purpose of Pivot Tables in Excel?",

        "What is Power BI used for?",

        "Tell me about yourself and why you want to become a Data Analyst.",
    ],

    "Business Analyst": [

        "What does a Business Analyst do?",

        "What is requirements gathering?",

        "What is the difference between functional and non-functional requirements?",

        "How would you analyze a business problem using data?",

        "Tell me about yourself and why you want to become a Business Analyst.",
    ],

    "AI/ML Engineer": [

        "What is Machine Learning?",

        "What is the difference between supervised and unsupervised learning?",

        "What is overfitting?",

        "What is the difference between AI, Machine Learning and Deep Learning?",

        "Tell me about yourself and why you want to become an AI/ML Engineer.",
    ],

    "Full Stack Developer": [

        "What is the difference between HTML, CSS and JavaScript?",

        "What is React?",

        "What is a REST API?",

        "What is Django?",

        "Tell me about yourself and why you want to become a Full Stack Developer.",
    ],

    "Cyber Security Analyst": [

        "What is Cyber Security?",

        "What is a firewall?",

        "What is phishing?",

        "What is the difference between authentication and authorization?",

        "Tell me about yourself and why you want to become a Cyber Security Analyst.",
    ],

    "General": [

        "Tell me about yourself.",

        "What are your strengths?",

        "What are your weaknesses?",

        "Where do you see yourself in five years?",

        "Why should we hire you?",
    ],
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

        "AI/ML Engineer": [
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

    career = request.GET.get(
        "career",
        ""
    )

    # --------------------------------
    # Start interview
    # --------------------------------

    if request.method == "GET":

        if career:

            request.session[
                "interview_career"
            ] = career

            request.session[
                "interview_question_index"
            ] = 0

            request.session[
                "interview_scores"
            ] = []

            request.session[
                "interview_completed"
            ] = False

        else:

            career = request.session.get(
                "interview_career",
                "General"
            )

    else:

        career = request.session.get(
            "interview_career",
            "General"
        )

    questions = INTERVIEW_QUESTIONS.get(
        career,
        INTERVIEW_QUESTIONS["General"]
    )

    question_index = request.session.get(
        "interview_question_index",
        0
    )

    # --------------------------------
    # POST answer
    # --------------------------------

    if request.method == "POST":

        answer = request.POST.get(
            "answer",
            ""
        ).strip()

        if question_index < len(questions):

            question = questions[
                question_index
            ]

            evaluation = evaluate_interview_answer(
                question,
                answer,
                career
            )

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

            request.session.modified = True

            # Next question
            question_index += 1

            request.session[
                "interview_question_index"
            ] = question_index

            request.session.modified = True

            # Completed
            if question_index >= len(questions):

                request.session[
                    "interview_completed"
                ] = True

                request.session.modified = True

                return redirect(
                    "interview_result"
                )

    # --------------------------------
    # Current question
    # --------------------------------

    if question_index >= len(questions):

        return redirect(
            "interview_result"
        )

    current_question = questions[
        question_index
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
            "question": current_question,
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