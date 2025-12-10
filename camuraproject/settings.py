

# from pathlib import Path
# import os
# from decouple import Config, RepositoryEnv

# BASE_DIR = Path(__file__).resolve().parent.parent

# ENVIRONMENT = os.environ.get("DJANGO_ENV", "development")

# if ENVIRONMENT == "production":
#     env_file = BASE_DIR / ".env.production"
# else:
#     env_file = BASE_DIR / ".env"


# config = Config(RepositoryEnv(env_file))



# SECRET_KEY = config("SECRET_KEY")
# SMS_API_KEY = config("SMS_API_KEY")
# SMS_SENDER = config("SMS_SENDER")
# SMS_MESSAGE = config("SMS_MESSAGE")


# # email setting 


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
# ADMIN_NOTIFICATION_EMAIL = config('ADMIN_NOTIFICATION_EMAIL')







# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# # BASE_DIR = Path(__file__).resolve().parent.parent


# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-yd!_0y5(2$9q74qyatztp!jqg0tu7%ie-%ej8c1^_b)u(zzl83'

# # SECURITY WARNING: don't run with debug turned on in production!

# DEBUG = True
# # DEBUG = False
# ALLOWED_HOSTS = ["camura.in", "www.camura.in", "127.0.0.1"]

# LOGIN_REDIRECT_URL = 'home'
# LOGOUT_REDIRECT_URL = 'home'
# LOGIN_URL = 'register'



# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
# CRISPY_TEMPLATE_PACK = "bootstrap5"


# RAZORPAY_KEY_ID = "rzp_test_eceD19siWPPSac"
# RAZORPAY_KEY_SECRET = "nvSfyM9NpNNSkZcjScFdhVq6"

# # Application definition

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # 'home',
#     'crispy_forms',
#     'crispy_bootstrap5',
#     'widget_tweaks',
#     'django.contrib.sitemaps',
#     'home.apps.HomeConfig',    #this is for create profile after user signup


# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'camuraproject.urls'

# TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [TEMPLATES_DIR],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#                 'home.context_processors.cart_count',    # this is for cart count
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'camuraproject.wsgi.application'


# # Database
# # https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db/db.sqlite3',
#     }
# }


# # Password validation
# # https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# # Internationalization
# # https://docs.djangoproject.com/en/5.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'Asia/Kolkata'

# USE_I18N = True

# USE_TZ = True


# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/5.2/howto/static-files/


# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_DIRS = [
#     BASE_DIR / 'static'
#     #os.path.join(BASE_DIR, 'static'),
# ]


# # STATIC_URL = "/static/"
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"
# # Default primary key field type
# # https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# from django.contrib.messages import constants as messages
# MESSAGE_TAGS = {
#     messages.ERROR: 'danger'
# }




"""
Django settings for camuraproject project.
"""

from pathlib import Path
import os
from decouple import Config, RepositoryEnv

# =========================
# Base directory
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Load environment file
# =========================
ENVIRONMENT = os.environ.get("DJANGO_ENV", "development")  # set to "production" on server

if ENVIRONMENT == "production":
    env_file = BASE_DIR / ".env.production"
else:
    env_file = BASE_DIR / ".env"

if os.path.exists(env_file):
    config = Config(RepositoryEnv(env_file))
else:
    raise RuntimeError(f"{env_file} not found. Cannot load configuration.")

# =========================
# Secret Key
# =========================
SECRET_KEY = config("SECRET_KEY")

# =========================
# Debug
# =========================
DEBUG = config('DEBUG', cast=bool, default=True)

# =========================
# Allowed Hosts
# =========================
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default="127.0.0.1").split(",")

# =========================
# Login URLs
# =========================
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'register'

# =========================
# Crispy forms
# =========================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =========================
# Razorpay keys
# =========================
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default="")
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default="")

# =========================
# Installed apps
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'django.contrib.sitemaps',
    'home.apps.HomeConfig',  # profile after signup
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================
# Root URL
# =========================
ROOT_URLCONF = 'camuraproject.urls'

# =========================
# Templates
# =========================
TEMPLATES_DIR = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.cart_count',  # cart count
            ],
        },
    },
]

# =========================
# WSGI Application
# =========================
WSGI_APPLICATION = 'camuraproject.wsgi.application'

# =========================
# Database
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db/db.sqlite3',
    }
}

# =========================
# Password validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =========================
# Internationalization
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# =========================
# Static & Media files
# =========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================
# Default primary key field
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# Messages
# =========================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {messages.ERROR: 'danger'}

# =========================
# SMS Settings'
# =========================
SMS_API_KEY = config("SMS_API_KEY", default="")
SMS_SENDER = config("SMS_SENDER", default="")
SMS_MESSAGE = config("SMS_MESSAGE", default="")

# =========================
# Email settings
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
ADMIN_NOTIFICATION_EMAIL = config('ADMIN_NOTIFICATION_EMAIL')
