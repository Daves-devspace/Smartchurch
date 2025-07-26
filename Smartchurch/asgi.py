"""
ASGI config for Smartchurch project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
# Smartchurch/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Smartchurch.routing import websocket_urlpatterns

# Import FastAPI app from your script
from scripture.routes.api import router as fastapi_router
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Smartchurch.settings")
django.setup()

# Set up FastAPI
fastapi_app = FastAPI()
fastapi_app.include_router(fastapi_router)

# Set up Django
django_app = get_asgi_application()

# Combine FastAPI + Django for HTTP
from starlette.routing import Mount
from starlette.applications import Starlette

http_app = Starlette(routes=[
    Mount("/api", app=fastapi_app),
    Mount("/", app=django_app),
])

# Final ASGI app
application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": URLRouter(websocket_urlpatterns)

    # "websocket": AuthMiddlewareStack(
    #     URLRouter(websocket_urlpatterns)
    # ),-when using auth
})
