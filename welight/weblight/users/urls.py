# users_microservice/urls.py

from django.contrib import admin
from rest_framework.routers import DefaultRouter
from users.views import (
    UserRegistration,
    SignInView,
    AuthenticateUserView,
    PasswordResetView,
    PasswordResetRequestView,
    UserViewSet,
)
from django.urls import path

app_name = "users"

user_router = DefaultRouter()
user_router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path('sign-up/', UserRegistration.as_view(), name='user_registration'),
    path('sign-in/', SignInView.as_view(), name='user_login'),
    path('verify-otp/', AuthenticateUserView.as_view(), name='verify_otp'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='reset_password_request'),
    path('password-reset/<str:token>', PasswordResetView.as_view(), name='reset_password'),
]

urlpatterns += user_router.urls
