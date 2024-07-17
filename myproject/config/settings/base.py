from pathlib import Path
from decouple import config
import pymysql
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-a3_d(puh2n+89zyudoz%)^cz14waicrb1$3$r+)1&y$p8-%0!w')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    'rest_framework',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF 미들웨어 확인
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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




WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# AWS 설정

import os

AWS_ACCESS_KEY_ID = os.getenv('AKIA2UC3AWOOPLLJY36R')
AWS_SECRET_ACCESS_KEY = os.getenv('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')
AWS_STORAGE_BUCKET_NAME = 'factorys'


# MySQL 데이터베이스 설정
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'NAME': config('DB_NAME', default='project'),
        'NAME': config('DB_NAME', default='images_db'),
        'USER': config('DB_USER', default='admin'),
        'PASSWORD': config('DB_PASSWORD', default='12345678'),
        'HOST': config('DB_HOST', default='ls-2fba5d616ed19fb5499c5ae6c43bf72bc772ca47.c9um400asul8.ap-northeast-2.rds.amazonaws.com'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'"
        }
    }
}

# Testing the connection
try:
    connection = pymysql.connect(
        host=config('DB_HOST', default='ls-2fba5d616ed19fb5499c5ae6c43bf72bc772ca47.c9um400asul8.ap-northeast-2.rds.amazonaws.com'),
        user=config('DB_USER', default='admin'),
        password=config('DB_PASSWORD', default='12345678'),
        database=config('DB_NAME', default='project'),
        port=int(config('DB_PORT', default='3306'))
    )
    print("Connection successful")
except pymysql.MySQLError as e:
    print(f"Error connecting to the database: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000', cast=lambda v: [s.strip() for s in v.split(',')])

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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='asdf71394@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='lqeypzafwverqymt')

# DRF 설정 Django 앱 추가 
# DEFAULT_RENDERER_CLASSES: 이 옵션은 콘텐츠 협상에 사용되는 기본 렌더러 클래스를 지정합니다. API 응답이 어떤 형식으로 직렬화될지를 결정합니다.
# DEFAULT_AUTHENTICATION_CLASSES: 이 옵션은 요청 인증에 사용되는 기본 인증 클래스를 설정합니다. API 뷰에 적용되는 인증 메커니즘을 정의합니다.
# DEFAULT_PERMISSION_CLASSES: 이 옵션은 권한 부여에 사용되는 기본 권한 클래스를 지정합니다. API 뷰에 적용되는 접근 제어 규칙을 결정합니다.
# DEFAULT_PAGINATION_CLASS: 이 옵션은 API 응답의 페이지네이션에 사용되는 기본 페이지네이션 클래스를 설정합니다. API 결과가 페이지로 나뉘어 표시되는 방식을 제어합니다.
# DEFAULT_FILTER_BACKENDS: 이 옵션은 API 데이터 필터링에 사용되는 기본 필터 백엔드를 지정합니다. API 클라이언트가 사용할 수 있는 필터링 옵션을 정의할 수 있습니다.
# DEFAULT_THROTTLE_CLASSES: 이 옵션은 요청 제한에 사용되는 기본 제한 클래스를 설정합니다. 클라이언트가 API에 요청을 할 수 있는 속도를 제한합니다.

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
      'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# settings.py

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Ensure your BASE_DIR is set appropriately.

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
