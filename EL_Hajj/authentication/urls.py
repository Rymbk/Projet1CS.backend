
from django.urls import path
from . import views

urlpatterns = [
    path('auth/login',views.login_user),
    path('auth/register',views.register,name='register'),
    path('auth/verification-email', views.send_verification_email),
    path('auth/verify-email', views.verify_email),
    path("auth/reset-password-email", views.send_reset_password_email),
    path("auth/reset-password", views.reset_password),
    path('auth/logout',views.logout_user,name='logout'),
    path("auth/profile/<str:email>",views.get_user_info),
    path("auth/update-profile",views.update_profile),
    path("auth/currently_user",views.get_currently_logged_user),
    path("auth/image_upload", views.image_upload),
    
    
]
