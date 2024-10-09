import base64
import json
from django.core.mail import EmailMessage
from dashboard.models import EmailAuthentication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_message_gmail_api(email: EmailMessage):
    authentication = EmailAuthentication.objects.first()
    if not authentication or not authentication.token:
        raise Exception('No credentials found')
    creds = Credentials.from_authorized_user_info(authentication.token, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        authentication.token = json.loads(creds.to_json())
        authentication.save()
    service = build('gmail', 'v1', credentials=creds)
    message = email.message()
    # The django EmailMessage doesn't store BCC addresses in the message itself, instead it just uses the field
    # when getting the list of recipients. To send a BCC with the gmail API we need to manually add the BCC addresses
    # to the message
    for b in email.bcc:
        # yes, this is the syntax to append multiple items
        message["bcc"] = b
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'raw': encoded_message
    }
    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    return send_message
