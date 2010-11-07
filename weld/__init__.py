"""
    Weld: A Gmail XMPP Gateway
    Copyright (C) 2010 Lance Stout
    This file is part of Weld.

    See the file LICENSE for copying permission.
"""

from weld.config import Config, load_config
from weld.gmail import Gmail
from weld.client import GmailClient
from weld.transport import GmailTransport

__version__ = '0.1.0'
