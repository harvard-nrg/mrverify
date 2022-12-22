import os
import string
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)
__dir__ = os.path.dirname(__file__)

class Notifier:
    def __init__(self, conf):
        self._conf = conf
        self._meta = dict()
        self._scopes = [
            'https://www.googleapis.com/auth/gmail.send'
        ]

    def add_report(self, report):
        self._report = report

    def add_meta(self, meta):
        self._meta = meta

    def message_body(self):
        email_template = os.path.join(__dir__, 'template.html')
        with open(email_template, 'r') as fo:
            template = string.Template(fo.read())
        session = self._meta['session']
        body = template.safe_substitute(
            message=f'{session} has errors. See attachment for details.'
        )
        return body

    def send(self):
        creds_file = os.path.join(self._conf.config_dir, 'credentials.json')
        token_file = os.path.join(self._conf.config_dir, 'token.json')
        logger.debug(creds_file)
        logger.debug(token_file)
        creds = None
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self._scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_file, self._scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            message = MIMEMultipart()

            # add message content
            content = MIMEText(self.message_body(), 'html')
            message.attach(content)

            # set To, From, and Subject
            sender = self._conf.query('$.Notifications.Gmail.sender')
            recipients = self._conf.query('$.Notifications.Gmail.recipients')
            logger.debug(sender)
            logger.info(f'sending report to {recipients}')
            message['To'] = ', '.join(recipients)
            message['From'] = sender
            message['Subject'] = '⚠️  scan verification errors'

            # add attachments
            if self._report:
                basename = os.path.basename(self._report)
                with open(self._report, 'rb') as fo:
                    part = MIMEApplication(
                        fo.read(),
                        Name=basename
                    )
                part['Content-Disposition'] = f'attachment; filename="{basename}"'
                message.attach(part)

            # base64 encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # send message
            create_message = {
                'raw': encoded_message
            }
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            logger.info(f'Gmail API Message Id: {send_message["id"]}')
        except HttpError as error:
            logger.error(f'Gmail API error occurred: {error}')
            send_message = None

