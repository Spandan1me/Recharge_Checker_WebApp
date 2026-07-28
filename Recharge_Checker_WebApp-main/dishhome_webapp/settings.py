import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security -----------------------------------------------------------
# Change SECRET_KEY before deploying. You can also set it via the
# DJANGO_SECRET_KEY environment variable instead of editing this file.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'change-this-to-a-long-random-string-before-you-deploy'
)

# Set DJANGO_DEBUG=False in production.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Comma-separated list, e.g. "192.168.1.50,dishhome-report.local"
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,192.168.53.71,192.168.13.147'
).split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dishhome_webapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dishhome_webapp.wsgi.application'

# --- Database -------------------------------------------------------------
# By default use a local SQLite file for quick local testing. If you want
# MySQL, set DJANGO_DB_ENGINE=django.db.backends.mysql and the related
# environment variables below.
DB_ENGINE = os.environ.get('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.environ.get('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.environ.get('DJANGO_DB_NAME', 'dishhome_reports'),
            'USER': os.environ.get('DJANGO_DB_USER', 'dishhome_user'),
            'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'change-me'),
            'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
            'PORT': os.environ.get('DJANGO_DB_PORT', '3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }

if os.environ.get('DB_SSL', 'False') == 'True':
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS']['ssl'] = {'ssl_mode': 'REQUIRED'}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

# If you later serve this behind HTTPS via nginx, set an env var, e.g.:
#   DJANGO_CSRF_TRUSTED_ORIGINS=https://report.yourdomain.com
_csrf_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

# Cookies are only sent over HTTPS once DEBUG is off (i.e. once you're on
# a real domain behind Nginx + Let's Encrypt). Keep DEBUG=True while
# testing over plain http:// on your LAN.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

