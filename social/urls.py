import os

from django.conf.urls import include, url
from django.views.generic import TemplateView
import django.contrib.auth.views
from social import views


urlpatterns = [
    url(r'^$', views.main_page, name='social-main'),
    # Change password
    url(r'^user/password$',  django.contrib.auth.views.password_change, {'post_change_redirect': '/', 'template_name': 'registration/changepw.html'}, name='social-user-changepw'),
    # reset password
    url(r'^user/reset/sent$', django.contrib.auth.views.password_reset_done, name='social-pwreset-done'),
    url(r'^user/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$', django.contrib.auth.views.password_reset_confirm, {'post_reset_redirect': 'social-pwreset-complete'}, name='social-pwreset-confirm'),
    url(r'^user/reset/complete$', django.contrib.auth.views.password_reset_complete, name='social-pwreset-complete'),
    url(r'^user/reset/$', django.contrib.auth.views.password_reset, {'post_reset_redirect': 'social-pwreset-done', 'template_name': 'registration/pwreset.html', 'email_template_name': 'registration/pwreset_email.html'}, name='social-pwreset'),

    url(r'^user/follow$', views.user_follow, name='social-user-follow'),
    url(r'^user/unfollow$', views.user_unfollow, name='social-user-unfollow'),

    url(r'^profile/$', views.user_profile, name='social-user-profile'),
    url(r'^delete/$', views.delete_account, name='social-delete-account'),
    url(r'^login/$', django.contrib.auth.views.login, name='social-auth-login'),
    url(r'^logout/$', views.logout_page, name='social-auth-logout'),
    url(r'^register/$', views.register_page, name='social-auth-register'),
    url(r'^register/success/$', TemplateView.as_view(template_name='registration/register_success.html'), name='social-auth-register-success'),
    url(r'^tag/$', views.tag_save_page, name='tag-form'),

    url(r'^users/$', views.users_list, name='social-users-list'),
    # Ajax
    url(r'^ajax/tag/autocomplete/$', views.ajax_tag_autocomplete, name='social-tag-autocomplete'),
    # Tag page
    url(r'^tags/(?P<tagname>[\w\+]+)/(?P<modeltype>\w+)$', views.tag_page, name='social-tag-page'),
]
