import json

import google.auth.exceptions
from django.core.management.base import BaseCommand
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from dashboard.models import EmailAuthentication

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class Command(BaseCommand):
    """ """

    def add_arguments(self, parser):
        parser.add_argument("credentials", help="location of credentials.json file")

    def handle(self, *args, **options):
        authentication = EmailAuthentication.objects.first()
        do_auth = True
        if not authentication:
            print("No email authentication credentials exist, creating")
            credentials = json.load(open(options["credentials"], "r"))
            authentication = EmailAuthentication.objects.create(credentials=credentials)

        if authentication.token:
            creds = Credentials.from_authorized_user_info(authentication.token, SCOPES)
            if not creds or not creds.valid:
                print("Credentials are invalid")
                if creds and creds.expired and creds.refresh_token:
                    print("Credentials are expired... refreshing")
                    try:
                        creds.refresh(Request())
                        authentication.token = json.loads(creds.to_json())
                        authentication.save()
                        do_auth = False
                    except google.auth.exceptions.RefreshError:
                        print("Refresh error, performing authentication workflow")
                        do_auth = True
                else:
                    print("Credentials are invalid, performing authentication workflow")
                    do_auth = True
            else:
                print("Credentials are valid")
                do_auth = False

        if do_auth:
            print("No valid authentication token exists, performing authentication workflow")
            print("Use the email indicated in README.md for this flow")
            flow = InstalledAppFlow.from_client_config(
                authentication.credentials, SCOPES, redirect_uri="http://localhost:8080/"
            )
            url, code = flow.authorization_url()
            url = input("Enter the URL you were redirected to: ")
            url = url.replace("http", "https")
            flow.fetch_token(authorization_response=url)
            creds = flow.credentials
            authentication.token = json.loads(creds.to_json())
            authentication.save()
            print("Authentication successful")
