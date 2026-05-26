"""
URL configuration for accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import password_reset as pr

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
    # Custom password reset with OTP: enter email → receive link + OTP → click link → enter OTP → reset
    path('password-reset/', pr.password_reset_request, name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', pr.password_reset_confirm_with_otp, name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),
]
