from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from account import views

urlpatterns = [
    # Change password
    path(
        "password",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("account-user-profile"), template_name="registration/changepw.html"
        ),
        name="account-user-changepw",
    ),
    # reset password
    path(
        "reset/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("account-pwreset-done"),
            template_name="registration/pwreset.html",
            email_template_name="registration/pwreset_email.html",
        ),
        name="account-pwreset",
    ),
    path(
        "reset/sent",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/pwreset_sent.html"),
        name="account-pwreset-done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("account-pwreset-complete"), template_name="registration/pwreset_confirm.html"
        ),
        name="account-pwreset-confirm",
    ),
    path(
        "reset/complete",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/pwreset_complete.html"),
        name="account-pwreset-complete",
    ),
    path("profile/", views.user_profile, name="account-user-profile"),
    path("accessrequest/", views.access_request, name="account-accessrequest"),
    path("delete/", views.delete_account, name="account-delete-account"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="account-login"),
    path("logout/", auth_views.LogoutView.as_view(), name="account-logout"),
    path("register/", views.register_page, name="account-register"),
    path(
        "register/success/",
        TemplateView.as_view(template_name="registration/register_success.html"),
        name="account-register-success",
    ),
]
