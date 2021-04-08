import asyncio
from queue import Queue

import asyncrequests
import websockets
from websockets import ConnectionClosed

from api import concurrency, Client
from api.data.pokemon import *
from api.data.session import *
from battle import Room


def hook_event(obj, name, default=lambda x, y: None):
    setattr(obj, name, default)
    obj.register_event_type(name)


class ShowdownApp(Client):

    def __init__(self):
        super().__init__()
        self.uri = "ws://sim.smogon.com:8000/showdown/websocket"
        self.socket = None
        self.alive = False

        self.team_container = TeamContainer("teams",
                                            lambda name: parse_named_info(name, [], unknown_species),
                                            lambda name: parse_named_info(name, [], unknown_item),
                                            lambda name: parse_named_info(name, [], unknown_ability),
                                            lambda name: Nature[name.upper()],
                                            lambda name: parse_named_info(name, [], lambda n: MoveInfo(n)))

        print(self.team_container.team_dict)

        self.user = default_user
        self.challstr = ""
        self.formats = []
        self.selected_format = None
        self.selected_team = None

        self.event_dispatchers = []  # GUI event dispatchers
        self.receive_bindings = {  # Other callbacks
            "challstr": [self.on_challstr_received],
            "formats": [self.on_formats_received],
            "updatesearch": [],
            "updateuser": [self.on_user_update]
        }

        self.rooms = []
        self.listened_room = None

        self.send_queue = Queue()

        self.send_queue.put(lambda: concurrency.with_callback(
            send=self.team_container.load_teams,
            callback=lambda x: self.dispatch("on_teams_loaded")
        ))

    def get_room(self, room_id: str) -> Room:
        for room in self.rooms:
            if room.room_id == room_id:
                return room

    def join_room(self, room_id: str):
        if room := self.get_room(room_id):
            return room
        else:
            room = Room(room_id, "", [])
            self.rooms.append(room)
            return room

    def listen_room(self, room_id):
        self.listened_room = self.join_room(room_id)

    async def wait_until_alive(self, futures):
        fs = futures.copy()
        fs.append(concurrency.wait_for(lambda: not self.alive))
        return (await asyncio.wait(fs=fs,
                                   return_when=asyncio.FIRST_COMPLETED))[0].pop().result()

    async def initialize(self):

        return await self.open()

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
            room = self
            parts = messages.split("\n|")
            if parts[0].startswith(">"):
                room = self.join_room(parts[0][1:])
            for msg in parts:
                if msg.startswith(">"):
                    continue
                if msg.startswith("|"):
                    msg = msg[1:]
                parts = msg.split("|")
                room.on_message_received(parts[0], parts[1:])

    def add_dispatcher(self, dispatcher):
        for key in self.receive_bindings.keys():
            event = f"on_receiving_{key}"
            hook_event(dispatcher, event)
        hook_event(dispatcher, "on_connection_lost")
        hook_event(dispatcher, "on_teams_loaded")
        self.event_dispatchers.append(dispatcher)

    def dispatch(self, event: str, *args):
        for dispatcher in self.event_dispatchers:
            dispatcher.dispatch(event, self, args)

    def dispatch_packet(self, event: str, *args):
        self.dispatch(f"on_receiving_{event}", *args)

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

    def select_team(self, name):
        self.selected_team = self.team_container[name]

    def select_format(self, name):
        for f in self.formats:
            if f.name == name:
                self.selected_format = f

    def find_battle(self, team, format: Format = None):  # TODO Team support
        print(format, team)
        if format is None:
            self.find_battle(team, self.selected_format) if self.selected_format is not None else None
        elif team is None and not format.is_random():
            self.find_battle(self.selected_team, format) if self.selected_team is not None else None
        else:
            battle_team = "null" if team is None else "]".join([pokemon.format() for pokemon in team])
            self.send(f"|/utm {battle_team}\n/search {format.name}")

    def load_info(self):
        pass

    def on_registered_message_received(self, header: str, values: List[str]):
        self.dispatch_packet(header, *values)

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
