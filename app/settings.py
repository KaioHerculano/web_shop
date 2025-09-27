"""
Django settings for app project.
"""

import os
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregue todas as suas variáveis de ambiente aqui, usando decouple.
SECRET_KEY = config("SECRET_KEY")

# A função config do decouple converte 'True'/'False' para booleano automaticamente
DEBUG = config("DEBUG", default=False, cast=bool)

# Carrega os hosts permitidos a partir de uma string separada por vírgulas no .env
# Ex: ALLOWED_HOSTS=localhost,127.0.0.1,meusite.com
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# Verificação de segurança para a SECRET_KEY
if not SECRET_KEY and not DEBUG:
    raise ValueError("A SECRET_KEY não foi definida no ambiente de produção!")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "brands",
    "cart",
    "orders",
    "products",
    "categories",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["app/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "app.context_processors.cart_items_count",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("SQL_DATABASE"),
        "USER": config("SQL_USER"),
        "PASSWORD": config("SQL_PASSWORD"),
        "HOST": config("SQL_HOST"),
        "PORT": config("SQL_PORT", cast=int),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Carregando variáveis de configuração do ambiente
EXTERNAL_API_BASE_URL = config("EXTERNAL_API_BASE_URL")
MERCHANT_WHATSAPP_NUMBER = config("MERCHANT_WHATSAPP_NUMBER")

# Configurações de Login/Logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
