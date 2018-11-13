from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template import loader

from dunya import settings


def email_admin_on_new_user(current_site: Site, user):
    """Send an email to site admins when a new user registers an account"""

    subject = 'New user registration - {}'.format(user.username)
    context = {'username': user.username, 'domain': current_site.domain}
    message = loader.render_to_string('registration/email_notify_admin.html', context)
    from_email = settings.NOTIFICATION_EMAIL_FROM
    recipients = [a for a in settings.NOTIFICATION_EMAIL_TO]
    send_mail(subject, message, from_email, recipients, fail_silently=True)


def email_user_on_account_approval(current_site: Site, user):
    """send an email to the user notifying them that their account is active"""

    subject = 'Your Dunya account has been activated'
    context = {'username': user.username, 'domain': current_site.domain}
    message = loader.render_to_string('registration/email_account_activated.html', context)
    from_email = settings.NOTIFICATION_EMAIL_FROM
    recipients = [user.email, ]
    send_mail(subject, message, from_email, recipients, fail_silently=True)


def email_admin_on_access_request(current_site: Site, user, justification):
    subject = 'New restricted acccess request - {}'.format(user.username)
    context = {'username': user.username, 'domain': current_site.domain, 'justification': justification}
    message = loader.render_to_string('registration/email_permission_request_notify_admin.html', context)
    from_email = settings.NOTIFICATION_EMAIL_FROM
    recipients = [a for a in settings.NOTIFICATION_EMAIL_TO]
    send_mail(subject, message, from_email, recipients, fail_silently=True)


def email_user_on_access_request_approval(current_site: Site, user, approved: bool):
    """notify a user that their access request has been approved or denied"""
    subject = 'Response to your Dunya access request'
    context = {'username': user.username, 'domain': current_site.domain}
    if approved:
        message = loader.render_to_string('registration/email_permission_request_approved.html', context)
    else:
        message = loader.render_to_string('registration/email_permission_request_denied.html', context)
    from_email = settings.NOTIFICATION_EMAIL_FROM
    recipients = [user.email, ]
    send_mail(subject, message, from_email, recipients, fail_silently=True)
