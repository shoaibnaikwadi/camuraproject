"""
WSGI config for camuraproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camuraproject.settings')

# application = get_wsgi_application()


import os
from decouple import Config, RepositoryEnv

# Absolute path to project root (where manage.py and .env are located)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to .env file
ENV_FILE = os.path.join(BASE_DIR, '.env')

# Load .env manually (fix for Apache not reading .env)
if os.path.exists(ENV_FILE):
    config = Config(RepositoryEnv(ENV_FILE))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camuraproject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
