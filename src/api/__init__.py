import asyncio
import os
import re
from queue import Queue
from typing import List

import asyncrequests
import websockets
from websockets import ConnectionClosed

from api import concurrency
from api.data.session import *


class ShowdownApp:

    def __init__(self):
        self.uri = "ws://sim.smogon.com:8000/showdown/websocket"
        self.socket = None
        self.alive = False

        self.user = default_user
        self.challstr = ""
        self.formats = []
        self.selected_format = None

        self.event_dispatchers = []  # GUI event dispatchers
        self.receive_bindings = {  # Other callbacks
            "challstr": [self.on_challstr_received],
            "formats": [self.on_formats_received],
            "updatesearch": [],
            "updateuser": [self.on_user_update]
        }

        self.send_queue = Queue()

    async def wait_until_alive(self, futures):
        fs = futures.copy()
        fs.append(concurrency.wait_for(lambda: not self.alive))
        return (await asyncio.wait(fs=fs,
                                   return_when=asyncio.FIRST_COMPLETED))[0].pop().result()

    async def open(self):
        print("opening")
        try:
            self.socket = await websockets.connect(self.uri)
        except OSError as error:
            print("Error while opening")
            print(error)
        self.alive = True
        print("open")
        return self.socket

    async def close(self):
        print("closing")
        self.alive = False

    async def listen(self):
        if self.socket is None:
            print("not opened")
            return
        if not self.socket.open:
            print("closed")  # TODO disconnect screen
            return
        try:
            messages = await self.socket.recv()
        except ConnectionClosed or OSError as error:
            print("disonnected", error)
        else:
            for msg in messages.split("\n|"):
                print("received", msg)
                if msg.startswith("|"):
                    msg = msg[1:]
                parts = msg.split("|")
                self.on_message_received(parts[0], parts[1:])

    def add_dispatcher(self, dispatcher):
        for key in self.receive_bindings.keys():
            event = f"on_receiving_{key}"
            setattr(dispatcher, event, lambda x, y: None)
            dispatcher.register_event_type(event)
        setattr(dispatcher, "on_connection_lost", lambda x, y: None)
        dispatcher.register_event_type("on_connection_lost")
        self.event_dispatchers.append(dispatcher)

    def dispatch(self, event: str, *args):
        for dispatcher in self.event_dispatchers:
            dispatcher.dispatch(f"on_receiving_{event}", self, args)

    async def send_async(self, message):
        print("send msg")
        await self.socket.send(message)
        print("sent")

    def send(self, message):
        print("sending", message)
        self.send_queue.put(lambda: self.send_async(message))

    def finish_login(self, response):
        print("body", response.body)
        d = json.loads(response.body[1:])
        self.send(f"|/trn {d['curuser']['username']},0,{d['assertion']}")

    def login_async(self):
        pass

    def login(self, username, password):
        print("login")
        self.send_queue.put(lambda: concurrency.with_callback(
            send=lambda: asyncrequests.post(url="https://play.pokemonshowdown.com/action.php", data={
                "act": "login",
                "name": username,
                "pass": password,
                "challstr": self.challstr
            }), callback=self.finish_login))

    def select_format(self, name):
        for f in self.formats:
            if f.name == name:
                self.selected_format = f

    def find_battle(self, format: Format = None, team=None):  # TODO Team support
        if format is None:
            return self.find_battle(self.selected_format) if self.selected_format is not None else None
        self.send(f"|/utm null\n/search {format.name}")

    def on_message_received(self, header: str, values: List[str]):
        bindings = self.receive_bindings.get(header)
        if bindings is not None:
            for callback in bindings:
                callback(values)
            self.dispatch(header, *values)

    def bind(self, **kwargs):
        for entry in kwargs:
            print(entry)
            self.receive_bindings.get(entry[0]).append(entry[1])

    def on_user_update(self, values: List[str]):

        avatar = values[2]
        if not os.path.isfile(f"sprite/trainer/{avatar}.png"):
            avatar = "red"

        self.user = user_from_json(nickname=values[0], logged_in=values[1] == "1", avatar=avatar, data=values[3])
        print("updated", self.user.avatar, self.user.logged_in, values[1] == "1", avatar)

    def on_formats_received(self, values: List[str]):
        self.formats = []
        category_pattern = re.compile(r",[0-9]")
        is_category = False
        for value in values:
            if is_category:
                is_category = False
            elif category_pattern.fullmatch(value):
                is_category = True
            else:
                format = Format(*value.split(","))
                self.formats.append(format)
                if self.selected_format is None:
                    print(format)
                    self.selected_format = format

    def on_challstr_received(self, values: List[str]):
        self.challstr = values[0] + "|" + values[1]
        self.login("Il_totore", "gamegie95740")