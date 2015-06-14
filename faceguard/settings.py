"""
Django settings for faceguard project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#l122zmplxer=^*t(wy3)+48y(l9&jr)h!v8mirv*r=9&&+z7v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

AUTHORIZE_URL = 'https://graph.facebook.com/oauth/authorize?'
ACCESS_TOKEN_URL = 'https://graph.facebook.com/v2.3/oauth/access_token?'
CLIENT_ID = '177316008955964'
CLIENT_APP_SECRET = 'a98cec4142c3cd8ed35800b48696f136'
GRANT_TYPE = 'client_credentials'
REDIRECT_URL = 'http://faceguard.herokuapp.com/facebook_login_success'
SENDER_EMAIL = 'milind.sakya@gmail.com'
# Application definition

INSTALLED_APPS = (
    'facebook',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'faceguard.urls'

WSGI_APPLICATION = 'faceguard.wsgi.application'

# These settings are needed to delete comments posted in user feed,
# pages etc. TODO Make sure it works for groups as well.
FACEBOOK_SCOPE = [
        'publish_actions',
        'publish_pages',
        'user_photos',
        'user_posts',
        'manage_pages',
        'user_about_me',
        'email'
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

import dj_database_url
DATABASES['default'] =  dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


import os
PROJECT_DIR=os.path.dirname(__file__)
STATIC_ROOT= os.path.join(PROJECT_DIR,'static_media/')
TEMPLATE_DIRS = (
    'templates',
)
