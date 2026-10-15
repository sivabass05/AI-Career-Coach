# AI Career Coach and Skill Development System

## Project Overview

AI Career Coach and Skill Development System is a Django-based web application designed to help students identify suitable career paths, evaluate their skills, improve their abilities, analyze resumes, practice interviews, and discover relevant job opportunities.

The system provides personalized career guidance based on the user's skills, interests, assessment results, resume information, and interview performance.

---

## Main Features

### 1. User Registration and Login
- Student registration
- Secure login and logout
- User-specific dashboard
- Authentication using Django

### 2. Student Profile
Students can maintain their:
- Full name
- Phone number
- Education
- College
- Graduation year
- Career goal

### 3. Skill Assessment
Students can:
- Select their skills
- Provide career interests
- Select fields they enjoy
- Receive a skill score
- Get a recommended career

### 4. Career Recommendation
The system analyzes the student's assessment information and provides a suitable career recommendation.

### 5. Learning Path
Provides career-oriented learning guidance based on the recommended career.

### 6. Resume Analyzer
Students can upload their resume in:
- PDF
- DOCX

The system analyzes the resume and provides:
- ATS score
- Detected skills
- Word count
- Sections found
- Action words
- Improvement suggestions

### 7. Mock Interview
Students can select a career and practice interview questions.

Supported career areas include:
- Java Developer
- Python Developer
- Data Analyst
- Business Analyst
- AI/ML Engineer
- Full Stack Developer
- Cyber Security Analyst
- General

The system evaluates:
- Technical knowledge
- Relevance
- Communication
- Overall performance

### 8. Interview Results
Students can view their mock interview performance and feedback.

### 9. Job Recommendation
The system recommends relevant job opportunities based on:
- Skills
- Career interest
- Career match

### 10. Admin Panel
The Django admin panel allows administrators to manage:
- Student Profiles
- User Skill Assessments
- Resumes
- Mock Interviews

---

## Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django

### Database
- MySQL

### Libraries / Packages
- Django REST Framework
- PyMySQL
- pypdf
- python-docx

---

## Project Structure

```text
backend/
│
├── backend/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── __init__.py
│
├── career_recommendation/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   └── ...
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── skill_assessment.html
│   ├── career_recommendation.html
│   ├── learning_path.html
│   ├── resume.html
│   ├── mock_interview.html
│   ├── interview_result.html
│   └── job_recommendation.html
│
├── media/
│
├── manage.py
├── requirements.txt
└── README.mdpython manage.py check
