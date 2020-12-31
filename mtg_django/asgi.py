"""
ASGI config for mtg_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from mtg.websocket_application import WebsocketClass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtg_django.settings')

django_application = get_asgi_application()
wsc = WebsocketClass()


async def application(scope, receive, send):

    if scope['type'] == 'http':
        # Let Django handle HTTP requests
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await wsc.websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
