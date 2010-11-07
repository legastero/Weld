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
        self.gmail = Gmail(config['email']['username'],
                           config['email']['password'])

        self.registerPlugin('xep_0030')
        self.registerPlugin('xep_0199')
        self.registerPlugin('gmail_notify')

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("disconnected", self.shutdown)
        self.add_event_handler("gmail_messages", self.recv_gmail)

    def start(self, event):
        self.sendPresence()
        self.getRoster()
        self.gmail.connect()
        self.plugin['gmail_notify'].checkEmail()

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

            if not email_from in self.config['email']['allowed']:
                log.debug("Received email from unallowed address.")
                continue

            log.debug("Received email from allowed address.")
            self.component.event('gmail_recv', {'to': self.config['owner'],
                                                'from': email_from,
                                                'subject': email['Subject'],
                                                'body': body})

    def send_gmail(self, to, subject, email):
        if email in self.config['email']['allowed']:
            self.gmail.send(to, subject, email)
            return True
        log.debug("Attempted to send email to unallowed address.")
        return False
