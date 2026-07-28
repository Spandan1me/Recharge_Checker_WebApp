import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dishhome_webapp.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'adminpass'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created: admin / adminpass')
else:
    print('Superuser already exists')
