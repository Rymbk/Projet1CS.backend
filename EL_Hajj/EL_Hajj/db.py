
# Replace the DATABASES section of your settings.py with this
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'EL_HAJJ_L',
    'USER': 'El_Hajj_db_owner',
    'PASSWORD': 'JagfjOWsq37w',
    'HOST':'ep-winter-cake-a2lxnvdu.eu-central-1.aws.neon.tech',
    'PORT': '5432',
    'OPTIONS': {
      'sslmode': 'require',
    },
  }
}