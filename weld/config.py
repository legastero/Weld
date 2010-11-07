"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

import sleekxmpp
from sleekxmpp.xmlstream import ElementBase, ET


def load_config(filename):
    with open(filename, 'r+') as conf_file:
        data = "\n".join([line for line in conf_file])
        config = Config(xml=ET.fromstring(data))
        return config


class ConfigClient(ElementBase):
    name = "client"
    namespace = "weld:config"
    interfaces = set(('owner', 'jid', 'password',
                      'server', 'port', 'allowed'))
    sub_interfaces = set(('jid', 'password', 'server', 'port'))

    def get_allowed(self):
        allowed = []
        for allowedXML in self.xml.findall('{%s}allow' % self.namespace):
            allowed.append(allowedXML.text)
        return allowed


class Config(ElementBase):
    name = "config"
    namespace = "weld:config"
    interfaces = set(('jid', 'password', 'server', 'port', 'clients'))
    sub_interfaces = interfaces
    subitem = (ConfigClient,)

    def get_clients(self):
        clients = []
        clientsXML = self.xml.findall('{%s}client' % self.namespace)
        for clientXML in clientsXML:
            client = ConfigClient(xml=clientXML, parent=None)
            clients.append(client)
        return clients
