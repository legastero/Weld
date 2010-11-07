"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

import os
import email
import logging
import smtplib
import imaplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart


log = logging.getLogger(__name__)


class Gmail(object):

    """
    Send and receive email from Gmail.
    """

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.smtp = None
        self.imap = None

    def connect(self):
        """
        Connect to the Gmail servers over SMTP and IMAP.

        NOTE: Don't connect too frequently (like during testing)
              or Google will disable your account from accessing
              from outside of the Gmail web interface. Use
              https://www.google.com/accounts/UnlockCaptcha
              to re-enable the account.
        """
        log.debug('GMAIL: Connecting to server')
        self.smtp = smtplib.SMTP("smtp.gmail.com", 587)
        self.smtp.starttls()
        self.smtp.login(self.__username, self.__password)

        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(self.__username, self.__password)

    def disconnect(self):
        """Close the SMTP and IMAP connections."""
        log.debug('GMAIL: Disconnecting from server')
        try:
            self.smtp.close()
            self.imap.close()
            self.imap.logout()
        except:
            log.error('GMAIL: Error disconnecting from server.')

    def send(self, to, subject, message, attachments=None):
        """
        Send an email. May also include attachments.

        to          -- The email recipient.
        subject     -- The email subject.
        message     -- The email body.
        attachments -- A list of file names to include.
        """
        if attachments is None:
            attachments = []
        msg = MIMEMultipart()
        msg.attach(MIMEText(message))
        for path in attachments:
            content_type, encoding = mimetypes.guess_type(path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, subtype = content_type.split('/', 1)

            with open(path, 'rb') as file:
                data = file.read()
                attachment = MIMEBase(main_type, subtype)
                attachment.set_payload(data)
                email.encoders.encode_base64(attachment)

            attachment.add_header('Content-Disposition',
                                  'attachment',
                                  filename=os.path.basename(path))
            msg.attach(attachment)

        msg['To'] = to
        msg['From'] = self.__username
        msg['Subject'] = subject

        log.debug('GMAIL: Sending email to %s' % msg['To'])
        errors = self.smtp.sendmail(self.__username, to, msg.as_string())

        return msg, errors

    def check(self, label='INBOX', senders=None):
        """
        Check for new messages.

        Arguments:
            label   -- The label/folder to check.
            senders -- Only look for messages from certain senders.
        """
        log.debug('GMAIL: Checking %s for %s' % (label, senders))

        _, count = self.imap.select(label)
        _, stats = self.imap.status(label, "(UNSEEN)")

        unread = int(stats[0].split()[2].strip(').,]'))
        if not unread:
            log.debug('GMAIL: No new messages.')
            return []

        messages = []
        if not senders:
            senders = ['(UNSEEN)']
        else:
            senders = ['(FROM "%s" UNSEEN)' % s for s in senders]
        for sender in senders:
            _, ids = self.imap.search(None, sender)
            ids = ids[0].split(' ')
            for email_id in ids:
                _, data = self.imap.fetch(email_id, '(UID RFC822)')
                msg = email.message_from_string(data[0][1])
                messages.append(email.message_from_string(data[0][1]))

        log.debug('GMAIL: Received %d messages.' % len(messages))
        return messages
