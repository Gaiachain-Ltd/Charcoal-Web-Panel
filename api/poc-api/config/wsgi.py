"""
WSGI config for poc_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""
import os
import sys

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior
# researchat directory.
app_path = os.path.dirname(os.path.abspath(__file__)).replace('/config', '')
sys.path.append(os.path.join(app_path, 'apps'))


# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
