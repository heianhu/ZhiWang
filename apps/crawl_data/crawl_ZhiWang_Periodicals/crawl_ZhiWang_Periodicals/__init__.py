import sys
import os
import django

from django.core.wsgi import get_wsgi_application

pathname = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.extend([pathname, ])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZhiWang.settings")
application = get_wsgi_application()

# # 能单独使用Django的models运行该脚本
#
# pathname = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, pathname)
# sys.path.insert(0, os.path.abspath(os.path.join(pathname, '../../..')))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZhiWang.settings")
# django.setup()
