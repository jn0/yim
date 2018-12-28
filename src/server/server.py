#!/usr/bin/env python3
'''
'''

import logging
import json
from websocket_server import WebsocketServer

from utils import ContextManager, Namespace

class WSServer(ContextManager):
    def __init__(self, **kw):
        self.env = Namespace(kw)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.root.level)
        self.clients = dict()

    def new_client(self, id_):
        raise NotImplementedError

    def lost_client(self, id_):
        raise NotImplementedError

    def lost_client(self, id_):
        raise NotImplementedError

    def dispatch_message(self, id_, message):
        raise NotImplementedError

    def add_client(self, client, server):
        self.log.debug('+client(%r, %r)', client, server)
        assert client['id'] not in self.clients, 'Client {!r} already here'.format(client)
        self.clients[client['id']] = client
        self.new_client(client['id'])

    def del_client(self, client, server):
        self.log.debug('-client(%r, %r)', client, server)
        assert client['id'] in self.clients, 'Client {!r} already gone'.format(client)
        self.lost_client(client['id'])
        self.clients.pop(client['id'])

    def get_message(self, client, server, message):
        self.log.debug('=message(%r, %r, %r)', client, server, message)
        assert client['id'] in self.clients, 'No client {!r} to get from'.format(client)
        self.dispatch_message(client['id'], message)

    def send(self, client, message):
        self.log.debug('=send(%r, %r, %r)', client, message, extra)
        assert client['id'] in self.clients, 'No client {!r} to send to'.format(client)
        self.server.send_message(client, message)

    def broadcast(self, message):
        self.log.debug('=broadcast(%r)', message)
        j = dict(text=message, sender=None)
        j = json.dumps(j)
        self.server.send_message_to_all(j)

    def serve(self):
        self.server = WebsocketServer(
            self.env.port,
            host = self.env.host,
            # loglevel = self.log.level,
        )
        self.server.set_fn_new_client(self.add_client)
        self.server.set_fn_client_left(self.del_client)
        self.server.set_fn_message_received(self.get_message)
        return self.server.run_forever()

#end class WSServer

class JSONWSServer(WSServer):
    def dispatch_message(self, id_, message):
        client = self.clients[id_]
        if not message:
            return
        j = json.loads(message)
        raise NotImplementedError

    def send(self, client, message, extra={}):
        if isinstance(message, dict):
            j = message
            j['sender'] = client
        elif isinstance(message, basestring):
            j = dict(text=message, sender=client)
        else:
            assert False, 'Bad message type {!r}'.format(message)
        assert 'text' in j, 'Bad message {!r}'.format(message)
        if extra:
            j.update(extra)
        super(JSONWSServer, self).send(client, json.dumps(j))

    def broadcast(self, message, extra={}):
        if isinstance(message, dict):
            j = message
        elif isinstance(message, basestring):
            j = dict(text=message)
        else:
            assert False, 'Bad message type {!r}'.format(message)
        assert 'text' in j, 'Bad message {!r}'.format(message)
        if extra:
            j.update(extra)
        super(JSONWSServer, self).broadcast( json.dumps(j))
#end class JSONWSServer

class ChatRoom(object):
    def __init__(self, name, initiator, server):
        self.name = name
        self.initiator = initiator
        self.server = server
        self.members = {initiator['id']: initiator}
        self.closed = False

    def __contains__(self, client):
        return client['id'] in self.members

    @property
    def empty(self):
        return len(self.members) == 0

    def join(self, client):
        if client not in self:
            self.members[client['id']] = client

    def gone(self, client):
        assert client in self, 'Client {!r} already gone'.format(client)
        self.members.pop(client['id'])
        if self.empty:
            self.close()
        return self

    def close(self):
        assert self.empty, 'Cannot close room {!r}'.format(self.name)
        self.closed = True

    def send(self, sender, text, extra):
        j = dict(text=text, sender=sender['id'], room=self.name)
        if extra:
            j.update(extra)
        for m in self.members:
            if m != sender['id']:
                self.server.send(self.members[m], j)
#end class ChatRoom

class ChatServer(JSONWSServer):
    def __init__(self, **kw):
        super(ChatServer, self).__init__(**kw)
        self.rooms = {}

    def new_client(self, id_):
        client = self.clients[id_]
        self.send(client, 'Welcome to the chat, client {}'.format(id_))
        room_list = ', '.join(self.rooms.keys())
        self.send(client, room_list)

    def lost_client(self, id_):
        client = self.clients[id_]
        self.broadcast('Client {} has gone'.format(id_))
        for r in self.rooms.keys():
            if self.rooms[r].gone(client).closed:
                self.rooms.pop(r)

    def dispatch_message(self, id_, message):
        client = self.clients[id_]
        if not message:
            return
        j = json.loads(message)

        text = j.get('text', None)
        if not text:
            return

        to = j.get('to', None)
        join, room = j.get('join', None), None
        extra = j.get('attributes', None)

        if join is not None:
            if join in self.rooms:
                self.rooms[join].join(client)
            else:
                self.rooms[join] = ChatRoom(join, client, self)
            room = self.rooms[join]

        if to is not None:
            if to in self.clients:
                extra['sender'] = client
                self.send(self.clients[to], text, extra)
            else:
                self.send(client, 'Cannot send to {!r}: no such client'.format(to))
        elif room is not None:
            room.send(client, text, extra)
        else:
            raise Exception('I dunno what U want')

#end class ChatServer

# vim: set ft=python ai et ts=4 sts=4 sw=4 colorcolumn=80: #
