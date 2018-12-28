#!/usr/bin/env python3
'''
'''

__VERSION__ = (0, 0, 0)
__VERSION_STRING__ = '.'.join(str(i) for i in __VERSION__)

__DEFAULT_HOST__ = '0.0.0.0'
__DEFAULT_PORT__ = 12345

import logging ; log = logging.getLogger('YIM-SERVER'
                                         if __name__ == '__main__'
                                         else __name__)

import sys
import server

from utils import AP

arg = AP(
    description='Yet Another Instant Messanger Server',
).add(
    '--version', action='version', version=__VERSION_STRING__,
    help='Version ({})'.format(__VERSION_STRING__)
).add(
    '-q', '--quiet', action='count', default=0
).add(
    '-v', '--verbose', action='count', default=0
).add(
    '-H', '--host', help='address to bind to',
    default=__DEFAULT_HOST__
).add(
    '-P', '--port', help='port to listen on',
    default=__DEFAULT_PORT__, type=int
).end_of_args()

def main(logLevel=logging.DEBUG):
    logging.basicConfig(
        level = logLevel,
    )
    if arg.verbose > arg.quiet:
        log.setLevel(logging.DEBUG)
    elif arg.verbose < arg.quiet:
        log.setLevel(logging.ERROR)
    try:
        log.info('START (%r:%r)', arg.host, arg.port)
        server_environment = dict(
            host = arg.host,
            port = arg.port,
        )
        with server.ChatServer(**server_environment) as srv:
            log.info('SERVING %r...', server_environment)
            srv.serve()
    finally:
        log.info('STOP')

if __name__ == '__main__':
    sys.exit(main())

# vim: set ft=python ai et ts=4 sts=4 sw=4 colorcolumn=80: #
