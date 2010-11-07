"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

import logging

import sleekxmpp
from sleekxmpp import ClientXMPP

from weld import Gmail


log = logging.getLogger(__name__)


class GmailClient(ClientXMPP):

    def __init__(self, component, config):
        ClientXMPP.__init__(self, config['jid'],
                                  config['password'])

        self.config = config
        self.component = component
        self.gmail = Gmail(config['jid'],
                           config['password'])

        self.register_plugin('xep_0030')
        self.register_plugin('gmail_notify')

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("disconnected", self.shutdown)

    def start(self, event):
        self.send_presence(ppriority='0')
        self.get_roster()
        self.gmail.connect()
        self.plugin['gmail_notify'].checkEmail()

        # Don't respond to mail notifications until after we've
        # connected to the server.
        self.add_event_handler("gmail_messages", self.recv_gmail)

    def shutdown(self, event):
        self.gmail.disconnect()

    def recv_gmail(self, event):
        emails = self.gmail.check()
        for email in emails:
            if not email.is_multipart():
                body = email.get_payload().strip()
            else:
                for part in email.get_payload():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload().strip()
                        break

            email_from = email['From']
            if '<' in email_from:
                email_from = email_from.split('<')[-1].split('>')[0]

            if not email_from in self.config['allowed']:
                log.debug("Received email from unallowed address.")
                continue

            log.debug("Received email from allowed address.")
            self.component.event('gmail_recv', {'to': self.config['owner'],
                                                'from': email_from,
                                                'subject': email['Subject'],
                                                'body': body})

    def send_gmail(self, to, subject, email):
        if to in self.config['allowed']:
            self.gmail.send(to, subject, email)
            return True
        log.debug("Attempted to send email to unallowed address: %s.")
        return False
