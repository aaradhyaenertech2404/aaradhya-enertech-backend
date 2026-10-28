import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Administrator User (Single Role)
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@aaradhyaenertech.com', 'admin123')
    print("Created administrator superuser: admin / admin123")
else:
    u = User.objects.get(username='admin')
    u.is_superuser = True
    u.is_staff = True
    u.set_password('admin123')
    u.save()
    print("Updated administrator: admin / admin123")

User.objects.filter(username='staff').delete()
User.objects.filter(username='superuser').delete()

print("Seed completed: Only admin account exists. 0 dummy records.")
