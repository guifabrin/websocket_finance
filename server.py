#!/usr/bin/env python

import json

import app.controllers
import base64
from app.repository import BaseRepository
from app.models import User
from app.controllers import auto_sync
import threading
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from app import database

database.create()

user_repository = BaseRepository(entity=User)


def receive_thread(message, websocket, user):
    app.controllers.process(json.loads(message), websocket, user)


class SimpleEcho(WebSocket):
    def handleMessage(self):
        email, password = base64.b64decode(self.request.path[1:].encode()).decode().split(':')
        user = user_repository.get_by('email', email)[0]
        if user.password == password:
            receive_thread(self.data, self, user)
            #new_thread = threading.Thread(target=receive_thread, args=(self.data, self, user))
            #new_thread.start()

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')



main_thread = threading.Thread(target=auto_sync)
main_thread.start()
server = SimpleWebSocketServer('', 8765, SimpleEcho)
server.serveforever()
