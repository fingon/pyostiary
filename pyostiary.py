#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
#
# $Id: pyostiary.py $
#
# Author: Markus Stenberg <fingon@iki.fi>
#
# Copyright (c) 2016 Markus Stenberg
#
# Created:       Thu Nov 10 21:06:39 2016 mstenber
# Last modified: Thu Nov 10 21:53:15 2016 mstenber
# Edit time:     34 min
#
"""Simple implementation of both Ostiary client and server in Python.

Configuration (subset) compatible, protocol compatible (hopefully).

Non features that are not implemented:

- kill when blacklist full

- kill command

- server-side configuration of various things in file (just edit
  defines in the .py, if you really must)

"""
import hashlib
import hmac
import os
import re
import socket
import time

SOCK_TIMEOUT = 5.0
CONNECTION_DELAY = 5.0
HASH_SIZE = 32
NONCE_SIZE = 32
ACTION_RE = re.compile('^ACTION="([^"]+)","([^"]+)"')


def open_socket(args, is_connect):
    flags = is_connect and socket.AI_PASSIVE or 0
    for res in socket.getaddrinfo(args.host, args.port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, flags):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
            if is_connect:
                s.connect(sa)
            else:
                s.bind(sa)
                s.listen(1)
            return s
        except socket.error as msg:
            pass
    raise Exception('Unable to open socket %s %s:%s' % (is_connect and "to" or "at",
                                                        args.host, args.port))


def run_client(args):
    s = open_socket(args, True)
    s.settimeout(SOCK_TIMEOUT)
    nonce = s.recv(HASH_SIZE)
    print('Got nonce %s' % nonce.encode('hex'))
    assert len(nonce) == HASH_SIZE
    buf = hmac.new(args.client, nonce, hashlib.sha256).digest()
    s.send(buf)
    print('Sent reply %s' % buf.encode('hex'))


def run_server(args):
    s = open_socket(args, False)
    while True:
        c, a = s.accept()
        try:
            c.settimeout(SOCK_TIMEOUT)
            nonce = os.urandom(NONCE_SIZE)
            c.sendall(nonce)
            buf = c.recv(HASH_SIZE)
            if len(buf) == HASH_SIZE:
                for line in open(args.server).readlines():
                    m = ACTION_RE.match(line)
                    if m is None:
                        continue
                    (key, cmd) = m.groups()
                    buf2 = hmac.new(key, nonce, hashlib.sha256).digest()
                    assert len(buf2) == len(buf)
                    if hmac.compare_digest(buf, buf2):
                        os.system('%s %s' % (cmd, a[0]))
        except socket.timeout:
            pass
        time.sleep(CONNECTION_DELAY)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--client', '-c', metavar='PASSWORD',
                   help='be client, contact server with the password')
    p.add_argument('--host', '--address', '-a',
                   help='server name/ip')
    p.add_argument('--port', '-p', type=int,
                   help='server port number to contact')
    p.add_argument('--server', '-s', metavar='CONFIGFILE',
                   help='be server, wait for connections (forever)')
    args = p.parse_args()
    assert args.port, 'A port number must be provided'
    if args.client:
        run_client(args)
    elif args.server:
        run_server(args)
