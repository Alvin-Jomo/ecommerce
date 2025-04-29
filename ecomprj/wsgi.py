"""
WSGI config for ecomprj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomprj.settings')

application = get_wsgi_application()


# import os
# import sys

# # Assuming your django settings file is at '/home/alvotheboss/evelyfreshventures/ecomprj/settings.py'
# # and your manage.py is at '/home/alvotheboss/evelyfreshventures/manage.py'
# path = '/home/alvotheboss/evelyfreshventures'
# if path not in sys.path:
#     sys.path.append(path)

# os.environ['DJANGO_SETTINGS_MODULE'] = 'ecomprj.settings'

# # Then:
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
