import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from bingo import routing as bingo_routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yaba_bingo.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo_routing.websocket_urlpatterns
        )
    ),
})