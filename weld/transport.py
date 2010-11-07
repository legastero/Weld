"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

import logging

import sleekxmpp
from sleekxmpp.componentxmpp import ComponentXMPP
from sleekxmpp.xmlstream import XMLStream

from weld import GmailClient


log = logging.getLogger(__name__)


class GmailTransport(ComponentXMPP):

    def __init__(self, config):
        ComponentXMPP.__init__(self, config['jid'],
                                     config['password'],
                                     config['server'],
                                     config['port'])
        self.config = config
        self.clients_config = {}
        self.clients = {}
        self.email_agents = {}

        self.register_plugin('xep_0030')

        self.auto_authorize = True
        self.auto_subscribe = True

        for client in config['clients']:
            self.clients_config[client['owner']] = client
            self.email_agents[client['owner']] = []
            for address in client['allowed']:
                addr = address[:]
                addr = '%s@%s' % (addr.replace('@', r'\40'), config['jid'])
                self.email_agents[client['owner']].append(addr)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('disconnected', self.shutdown)
        self.add_event_handler('killed', self.shutdown)
        self.add_event_handler('got_online', self.online, threaded=True)
        self.add_event_handler('got_offline', self.offline, threaded=True)
        self.add_event_handler('gmail_recv', self.send_message, threaded=True)
        self.add_event_handler('message', self.recv_message, threaded=True)
        self.add_event_handler('disco_info_request', self.disco, threaded=True)

    def disco(self, iq):
        self.plugin['xep_0030'].handle_disco_info(iq, True)

    def start(self, event):
        for client in self.clients_config:
            self.sendPresence(pto=client)
            self.sendPresence(pto=client, ptype='probe')
            for agent in self.email_agents[client]:
                self.sendPresence(pto=client, pfrom=agent)

    def shutdown(self, event):
        log.debug("Shutting down gateway.")
        for client in self.clients:
            self.clients[client].disconnect()
            self.sendPresence(pto=client,
                              pfrom=self.config['jid'],
                              ptype='unavailable')
            for agent in self.email_agents[client]:
                self.sendPresence(pto=client,
                                  pfrom=agent,
                                  ptype='unavailable')

    def online(self, presence):
        config = self.clients_config.get(presence['from'].bare, None)
        client = self.clients.get(presence['from'].bare, None)
        if config is not None and client is None:
            client = GmailClient(self, config)
            self.clients[config['owner']] = client

            log.debug("Starting Gmail client for %s" %
            presence['from'].bare)
            if config['server']:
                conn = client.connect((config['server'], config['port']))
            else:
                conn = client.connect()
            if conn:
                client.process(threaded=True)

    def offline(self, presence):
        client = self.clients.get(presence['from'].bare, None)
        if client:
            client.disconnect()
            del self.clients[presence['from'].bare]

    def send_message(self, event):
        msg = self.Message()
        msg['to'] = event['to']
        msg['from'] = '%s@%s' % (event['from'].replace('@', r'\40'),
                                 self.config['jid'])
        msg['subject'] = event['subject']
        msg['body'] = event['body']
        msg.send()

    def recv_message(self, msg):
        if msg['type'] not in ['normal', 'chat']:
            return

        sender = msg['from'].bare
        if sender in self.clients:
            email = str(msg['to']).split('@')[0]
            email = "@".join(email.split(r'\40'))
            email = email.split("<")[-1].split(">")[0]
            result = self.clients[sender].send_gmail(email,
                                                     msg['subject'],
                                                     msg['body'])
            if result:
                return
        msg.reply().error()
        msg['error']['code'] = '403'
        msg['error']['type'] = 'cancel'
        msg['error']['condition'] = 'forbidden'
        msg.send()
