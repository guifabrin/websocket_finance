#!/usr/bin/env python

import asyncio
import websockets
import json

import app.controllers
import base64
from app.repositories.base_repository import BaseRepository
from app.models import User, Notification
from app.controllers import auto_sync
import threading

user_repository = BaseRepository(entity=User)


def receive_thread(message, websocket, user):
    app.controllers.process(json.loads(message), websocket, user)


from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket


class SimpleEcho(WebSocket):

    def handleMessage(self):
        email, password = base64.b64decode(self.request.path[1:].encode()).decode().split(':')
        user = user_repository.get_by('email', email)[0]
        if user.password == password:
            x = threading.Thread(target=receive_thread, args=(self.data, self, user))
            x.start()

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


x = threading.Thread(target=auto_sync)
x.start()
server = SimpleWebSocketServer('', 8765, SimpleEcho)
server.serveforever()
