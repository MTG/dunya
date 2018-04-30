from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from account import views

urlpatterns = [
    # Change password
    url(r'^password$', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('account-user-profile'),
                                                             template_name='registration/changepw.html'),
        name='account-user-changepw'),
    # reset password
    url(r'^reset/$', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('account-pwreset-done'),
                                                          template_name='registration/pwreset.html',
                                                          email_template_name='registration/pwreset_email.html'),
        name='account-pwreset'),
    url(r'^reset/sent$', auth_views.PasswordResetDoneView.as_view(template_name='registration/pwreset_sent.html'),
        name='account-pwreset-done'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('account-pwreset-complete'),
                                                    template_name='registration/pwreset_confirm.html'),
        name='account-pwreset-confirm'),
    url(r'^reset/complete$',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/pwreset_complete.html'),
        name='account-pwreset-complete'),
    url(r'^profile/$', views.user_profile, name='account-user-profile'),
    url(r'^delete/$', views.delete_account, name='account-delete-account'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html'), name='account-login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='account-logout'),
    url(r'^register/$', views.register_page, name='account-register'),
    url(r'^register/success/$', TemplateView.as_view(template_name='registration/register_success.html'),
        name='account-register-success'),
]
