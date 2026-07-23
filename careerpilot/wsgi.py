"""
WSGI config for careerpilot project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys
import traceback

# Add the project root directory to the sys.path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerpilot.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    error_trace = traceback.format_exc()
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f"WSGI Setup Failed:\n\n{error_trace}".encode('utf-8')]

# Expose app for Vercel Serverless
app = application
