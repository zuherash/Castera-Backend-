from .settings import *
import os

# Use PostgreSQL database from Docker for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'castera_db_main'),
        'USER': os.environ.get('POSTGRES_USER', 'castera_user_main'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'castera_pass_main'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'TEST': {
            'NAME': os.environ.get('POSTGRES_TEST_DB', 'castera_test'),
        },
    }
}

# Simplify password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use in-memory channel layer for channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
