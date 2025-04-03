from django.urls import path
from registration.consumers import  TirageConsumer

websocket_urlpatterns = [
    path('ws/tirage/', TirageConsumer.as_asgi()),
]