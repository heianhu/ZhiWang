import sys
import os
import django

from django.core.wsgi import get_wsgi_application

pathname = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.extend([pathname, ])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZhiWang.settings")
application = get_wsgi_application()

