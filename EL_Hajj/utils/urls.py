from django.urls import path
from . import views

urlpatterns = [
    path("utils/passwords", views.gen_passwords)
]
