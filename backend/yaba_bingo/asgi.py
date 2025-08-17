import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# 1. Configure Django's settings FIRST.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yaba_bingo.settings")
django.setup()

# 2. NOW it is safe to import your application's code.
from channels.auth import AuthMiddlewareStack
from bingo import routing as bingo_routing

# 3. Define the application.
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo_routing.websocket_urlpatterns
        )
    ),
})