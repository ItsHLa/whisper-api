import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Whisper.settings')

django_asgi_app = get_asgi_application()
from a_rtchat.routes import chat_routes

application = ProtocolTypeRouter({
    "http" : django_asgi_app,
    # 'websocket' : AuthMiddlewareStack(
    #     URLRouter(
    #         chat_routes
    #     )
    # )
})
