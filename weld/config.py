"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

import sleekxmpp
from sleekxmpp.xmlstream import ElementBase, ET


def load_config(filename):
    """
    Create a configuration stanza object from
    the given file's contents.

    Arguments:
        filename -- Name of the config file.
    """
    with open(filename, 'r+') as conf_file:
        data = "\n".join([line for line in conf_file])
        config = Config(xml=ET.fromstring(data))
        return config


class ConfigClient(ElementBase):

    """
    Configuration information for a single, monitored
    email address.

    Only messages sent to or received from addresses
    included in <allow> elements will be accepted.

    Example stanza:
        <client owner="user@localhost">
          <jid>example@gmail.com</jid>
          <password>hunter2</password>

          <allow>user@example.com</allow>
        </client>

    Stanza Interface:
        owner    -- The JID that will be sending/receiving messages.
        jid      -- The Gmail account username.
        password -- The Gmail account password.
        allowed  -- A list of whitelisted email addresses.
    """

    name = "client"
    namespace = "weld:config"
    interfaces = set(('owner', 'jid', 'password', 'allowed'))
    sub_interfaces = set(('jid', 'password', 'server', 'port'))

    def get_allowed(self):
        """
        Return the list of accepted email addresses.
        """
        allowed = []
        for allowedXML in self.xml.findall('{%s}allow' % self.namespace):
            allowed.append(allowedXML.text)
        return allowed


class Config(ElementBase):

    """
    Connection information for the gateway, and config data
    for all monitored email addresses.

    Example stanza:
        <config>
          <jid>email.localhost</jid>
          <server>localhost</server>
          <port>8888</port>

          <client>....</client>
          <client>....</client>
        </config>

    Stanza Interface:
        jid      -- Component JID for the gateway.
        password -- Component secret.
        server   -- Server hosting the gateway component.
        port     -- Port to connect to the server.
        clients  -- List of client configuration stanzas.
    """

    name = "config"
    namespace = "weld:config"
    interfaces = set(('jid', 'password', 'server', 'port', 'clients'))
    sub_interfaces = interfaces
    subitem = (ConfigClient,)

    def get_clients(self):
        """Return list of client configurations."""
        clients = []
        clientsXML = self.xml.findall('{%s}client' % self.namespace)
        for clientXML in clientsXML:
            client = ConfigClient(xml=clientXML, parent=None)
            clients.append(client)
        return clients
