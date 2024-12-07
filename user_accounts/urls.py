from django.urls import path

from .views import RegisterView, LoginView, VerifyOTPView, SendOTPView


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
]
