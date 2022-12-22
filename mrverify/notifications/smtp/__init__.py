import os
import string
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

logger = logging.getLogger(__name__)
__dir__ = os.path.dirname(__file__)

class Notifier:
    def __init__(self, conf):
        self._conf = conf
        self._meta = dict()

    def add_report(self, report):
        self._report = report

    def add_meta(self, meta):
        self._meta = meta

    def send(self):
        email_template = os.path.join(__dir__, 'template.html')
        with open(email_template, 'r') as fo:
            template = string.Template(fo.read())
        session = self._meta['session']
        message = template.safe_substitute(message=f'{session} has errors. See attachment for details.')
        sender = self._conf.query('$.Notifications.SMTP.sender')
        recipients = self._conf.query('$.Notifications.SMTP.recipients')
        msg = MIMEMultipart()
        msg['Subject'] = '⚠️  scan verification errors'
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        body = MIMEText(message, 'html')
        msg.attach(body)
        if self._report:
            basename = os.path.basename(self._report)
            with open(self._report, 'rb') as fo:
                part = MIMEApplication(
                    fo.read(),
                    Name=basename
                )
            part['Content-Disposition'] = f'attachment; filename="{basename}"'
            msg.attach(part)
        server = self._conf.query(
            '$.Notifications.SMTP.server',
            default='localhost'
        )
        smtp = smtplib.SMTP(server)
        smtp.connect()
        smtp.sendmail(
            sender,
            recipients,
            msg.as_string()
        )
        smtp.close()

