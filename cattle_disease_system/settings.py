"""
Django settings for cattle_disease_system project.

This system implements an Early Disease Prediction and Veterinary 
Recommendation System for Cattle Using Machine Learning.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env (for EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, etc.)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

# SECURITY WARNING: keep the secret key secret!
# The real key lives in .env (gitignored). The fallback below is for local
# development only - it is deliberately marked insecure so it can never be
# mistaken for a production key.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-local-dev-only-set-DJANGO_SECRET_KEY-in-env',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'crispy_forms',  # Removed - not needed
    # 'crispy_bootstrap5',  # Removed - not needed
    
    # Custom apps
    'landing',
    'accounts',
    'farmers',
    'vets',
    'ministry',
    'cases',
    'ml_engine',
    'maps',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cattle_disease_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ministry.context_processors.ministry_sidebar_context',
                'farmers.context_processors.farmer_dashboard_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'cattle_disease_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
#
# SQLite by default, so the project runs straight after a clone with no
# database setup. To use PostgreSQL instead, put this in your .env:
#
#     DB_ENGINE=postgresql
#     POSTGRES_DB=cattle_disease_db
#     POSTGRES_USER=Admin_Ree
#     POSTGRES_PASSWORD=your-password-here
#
# No credential has a hardcoded default any more - PostgreSQL reads them
# all from the environment.

if os.environ.get('DB_ENGINE', 'sqlite').lower().startswith('post'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'cattle_disease_db'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    # Use regional variants to avoid Django's built-in placeholder locales for 'sn'/'nd'
    # that ship with invalid Plural-Forms headers (plural=EXPRESSION).
    ('sn-zw', 'Shona'),
    ('nd-zw', 'Ndebele'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Africa/Harare'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:redirect_after_login'
LOGOUT_REDIRECT_URL = 'landing:home'

# ML Model Paths
ML_MODEL_PATH = BASE_DIR / 'best_disease_model.pkl'
LABEL_ENCODER_PATH = BASE_DIR / 'label_encoder.pkl'
FEATURE_NAMES_PATH = BASE_DIR / 'feature_names.pkl'
PREPROCESSOR_PATH = BASE_DIR / 'preprocessor.pkl'  # Added for feature preprocessing

# Zimbabwe Provinces
ZIMBABWE_PROVINCES = [
    ('Bulawayo', 'Bulawayo'),
    ('Harare', 'Harare'),
    ('Manicaland', 'Manicaland'),
    ('Mashonaland Central', 'Mashonaland Central'),
    ('Mashonaland East', 'Mashonaland East'),
    ('Mashonaland West', 'Mashonaland West'),
    ('Masvingo', 'Masvingo'),
    ('Matabeleland North', 'Matabeleland North'),
    ('Matabeleland South', 'Matabeleland South'),
    ('Midlands', 'Midlands'),
]

# Disease Severity Thresholds (used for confidence-based escalation only)
# Severity is primarily disease-based (DISEASE_SEVERITY); these are used when
# confidence is low to escalate (e.g. low confidence → at least SEVERE).
SEVERITY_THRESHOLDS = {
    'NON_SEVERE': 0.40,  # Confidence >= 0.40 → no escalation
    'SEVERE': 0.22,      # Below 0.40: escalate to at least SEVERE
    'CRITICAL': 0.0,     # Below 0.22: escalate to at least SEVERE (or CRITICAL if disease is dangerous)
}

# Disease-based severity: dangerous nature of disease drives base severity.
# Confidence is used only to escalate when model is uncertain (low confidence → at least SEVERE).
# Keys must match model label_encoder class names (26 diseases).
DISEASE_SEVERITY = {
    'foot_and_mouth': 'CRITICAL',
    'rift_valley_fever': 'CRITICAL',
    'blackleg': 'SEVERE',
    'listeriosis': 'SEVERE',
    'mastitis': 'SEVERE',
    'calf_pneumonia': 'SEVERE',
    'trypanosomosis': 'SEVERE',
    'infectious_bovine_rhinotracheitis': 'SEVERE',
    'schmallen_berg_virus': 'SEVERE',
    'acetonaemia': 'NON_SEVERE',
    'bloat': 'NON_SEVERE',
    'calf_diphtheria': 'NON_SEVERE',
    'coccidiosis': 'NON_SEVERE',
    'cryptosporidiosis': 'NON_SEVERE',
    'displaced_abomasum': 'NON_SEVERE',
    'fatty_liver_syndrome': 'NON_SEVERE',
    'fog_fever': 'NON_SEVERE',
    'foot_rot': 'NON_SEVERE',
    'gut_worms': 'NON_SEVERE',
    'liver_fluke': 'NON_SEVERE',
    'necrotic_enteritis': 'NON_SEVERE',
    'peri_weaning_diarrhoea': 'NON_SEVERE',
    'ragwort_poisoning': 'NON_SEVERE',
    'rumen_acidosis': 'NON_SEVERE',
    'traumatic_reticulitis': 'NON_SEVERE',
    'wooden_tongue': 'NON_SEVERE',
}

# Vet Assignment Radius (in kilometers)
VET_SEARCH_RADIUS = 50  # Search for vets within 50km

# Email (for password reset) – sends reset link + OTP to the registered user's email
# For real emails: copy .env.example to .env and set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD.
# Gmail: use an App Password (Google Account → Security → 2-Step Verification → App passwords).
_use_smtp = bool(os.environ.get('EMAIL_HOST_USER') and os.environ.get('EMAIL_HOST_PASSWORD'))
if _use_smtp:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', f'CattleCare AI <{EMAIL_HOST_USER}>')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'CattleCare AI <noreply@cattlecare.gov.zw>'

# Cache (for OTP storage during password reset)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
PASSWORD_RESET_OTP_TIMEOUT = 600  # 10 minutes
