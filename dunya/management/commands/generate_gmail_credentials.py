import json

from django.core.management.base import BaseCommand

from dashboard.models import EmailAuthentication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class Command(BaseCommand):
    """
    """

    def add_arguments(self, parser):
        parser.add_argument('credentials', help='location of credentials.json file')

    def handle(self, *args, **options):
        authentication = EmailAuthentication.objects.first()
        if not authentication:
            print("No email authentication credentials exist, creating")
            credentials = json.load(open(options['credentials'], 'r'))
            authentication = EmailAuthentication.objects.create(credentials=credentials)

        if authentication.token:
            creds = Credentials.from_authorized_user_info(authentication.token, SCOPES)
            if not creds or not creds.valid:
                print("Credentials are invalid")
                if creds and creds.expired and creds.refresh_token:
                    print("Credentials are expired... refreshing")
                    creds.refresh(Request())
                    authentication.token = json.loads(creds.to_json())
                    authentication.save()
            else:
                print("Credentials are valid")
        else:
            print("No authentication token exists, performing authentication workflow")
            print("Use the email indicated in README.md for this flow")
            flow = InstalledAppFlow.from_client_config(authentication.credentials, SCOPES)
            creds = flow.run_local_server(port=0)
            authentication.token = json.loads(creds.to_json())
            authentication.save()