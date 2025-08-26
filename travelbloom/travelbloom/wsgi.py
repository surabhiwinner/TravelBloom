import os
import sys
import traceback

print("🚀 WSGI loading...")

# ✅ point to the correct nested settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelbloom.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ Django settings loaded successfully")
except Exception:
    print("❌ WSGI failed to load Django settings:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise
print("🚀 WSGI loaded successfully")