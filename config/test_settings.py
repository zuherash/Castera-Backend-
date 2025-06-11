from .settings import *

# Use PostgreSQL database from Docker for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castera_db_main',
        'USER': 'castera_user_main',
        'PASSWORD': 'castera_pass_main',
        'HOST': 'db',
        'PORT': '5432',
        'TEST': {
            'NAME': 'castera_test',
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
