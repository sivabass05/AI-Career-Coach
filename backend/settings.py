from pathlib import Path
import os

from dotenv import load_dotenv


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# SECURITY
# ---------------------------------------------------------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-key-for-local-development"
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


# ---------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",

    # Local app
    "career_recommendation",
]


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------
# URL CONFIGURATION
# ---------------------------------------------------------
ROOT_URLCONF = "backend.urls"


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------
# WSGI
# ---------------------------------------------------------
WSGI_APPLICATION = "backend.wsgi.application"


# ---------------------------------------------------------
# DATABASE - MYSQL
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",

        "NAME": os.getenv(
            "MYSQL_NAME",
            "my_django_db"
        ),

        "USER": os.getenv(
            "MYSQL_USER",
            "root"
        ),

        "PASSWORD": os.getenv(
            "MYSQL_PASSWORD",
            ""
        ),

        "HOST": os.getenv(
            "MYSQL_HOST",
            "localhost"
        ),

        "PORT": os.getenv(
            "MYSQL_PORT",
            "3306"
        ),

        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}


# ---------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ---------------------------------------------------------
# MEDIA FILES
# ---------------------------------------------------------
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------
# DEFAULT PRIMARY KEY
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------
# LOGIN / LOGOUT
# ---------------------------------------------------------
LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/dashboard/"

LOGOUT_REDIRECT_URL = "/"


# ---------------------------------------------------------
# FILE UPLOAD SETTINGS
# ---------------------------------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024


# ---------------------------------------------------------
# DJANGO REST FRAMEWORK
# ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# ---------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------
# These are suitable for local development.
# For production deployment, we will configure them separately.

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"