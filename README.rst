Weld: Gmail + XMPP
==================

The similarity between email addresses and XMPP JIDs is often noted in
introductory texts to XMPP, and there have been claims that XMPP can serve as an
email replacement (e.g. Google Wave). Weld takes the next step in merging email
and XMPP systems.

Converting emails into XMPP stanzas is a complex issue due to the various MIME
types, multipart emails, various headers, etc. Weld sidesteps that issue by
assuming that content is treated the same way in emails as it is in XMPP message
stanzas: a single, plain text message with an optional subject.

For example, an email such as::

    From: user@example.com
    To: weldaddr@example.com
    Subject: Mapping an email to an XMPP message

    Just some plain text content.

will be turned into an XMPP message like this::

    <message to="welduser@example.com"
             from="user\40example.com@weld.example.com">
      <subject>Mapping an email to an XMPP message</subject>
      <body>Just some plain text content.</body>
    </message>

Weld converts email addresses to valid JIDs by replacing the @ character
with the escape sequence `\\40`. Messages sent to these JIDs will be sent
as emails.

To make listening for new emails easier, Weld works with Gmail using Google's
new mail notification stanzas. A new XMPP client is created for each email
address monitored by Weld to listen for the new message notice. The message
is then retrieved via IMAP and converted into an XMPP stanza.

But Wait, There's More!
-----------------------
Weld can also work as an SMS gateway by sending and receiving messages from special
email addresses from wireless providers (see the `full list`_). For example, Alltel users can send and
receive text messages from 5555555555@message.alltel.com. In fact, getting this
functionality was the whole point of creating Weld in the first place.

.. _`full list`: http://en.wikipedia.org/wiki/List_of_SMS_gateways
