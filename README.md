# pyostiary

Minimal implementation of [Ostiary](http://ingles.homeunix.net/software/ost/) client/server in Python 2/3.

## Usage example given the sample configuration file

Start local server

    ./pyostiary.py -s pyostiary.cfg -p 12345

Prod it with client

    ./pyostiary.py -c foopassword -p 12345

foo ::1 (or 127.0.0.1 if not IPv6 enabled host) should ensue..

## Why new implementation?

The existing C implementation was relatively big, but not yet available on
the few platforms I care about. The options were to maintain some arbitrary
arm binaries, or use the Python2/3 already available on the platform. The
choice was easy enough.

## Non features that are not implemented

- kill when blacklist full

- kill command

- server-side configuration of various things in file (just edit
  defines in the .py, if you really must)

## Features that are not in last C version I checked

- IPv6 support
