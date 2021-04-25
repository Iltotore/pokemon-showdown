from typing import List, Optional, Dict, Callable, Any

from api import Client
from battle.entity import Player, Pokemon, SentPokemon, StatusEffect, Weather


class State:
    pass


State.PREVIEW, State.BATTLING = State(), State()


class End(State):

    def __init__(self, winner: Optional[Player]):
        self.winner = winner


class Battle(Client):

    def __init__(self, player: Optional[Player], opponent: Optional[Player],
                 parsers: Dict[str, Callable[[List[str]], Any]],
                 state: State = State.PREVIEW,
                 weather: Optional[Weather] = None):
        super().__init__()
        self.player = player
        self.opponent = opponent
        self.parsers = parsers
        self.state = state
        self.weather = weather

        # TODO https://github.com/smogon/pokemon-showdown/blob/master/sim/SIM-PROTOCOL.md#minor-actions
        self.receive_bindings = {
            "teampreview": lambda _: setattr(self, "state", State.PREVIEW),
            "start": lambda _: setattr(self, "state", State.BATTLING),
            "tie": lambda _: self.finish(None),
            "win": lambda values: self.finish(self.get_player(values[0])),
            "player": lambda values: (
                setattr(self, "player" if values[0] == "p1" else "opponent", Player.deserialize(*values[1:]))
            ),
            "poke": lambda values: (
                self.players()[int(values[0])].team.append(Pokemon.deserialize(values[1], values[2], **parsers)) if
                self.players()[int(values[0])] else None
            ),
            "faint": lambda values: self.get_player(values[0]).sent.faint(),
            "-status": lambda values: (
                setattr(self.get_sent_pokemon(values[0]).pokemon, "status_effect", StatusEffect(values[1]))
            ),
            "-damage": lambda values: (
                pokemon := self.get_sent_pokemon(values[0]),
                health_and_max := values[1].split(" ")[0].split("/"),
                setattr(pokemon, "health", int(health_and_max[0])),
                setattr(pokemon, "max_health", int(health_and_max[1]))
            ),
            "-weather": lambda values: setattr(self, "weather", Weather(values[0])),
            "-curestatus": lambda values: setattr(self.get_sent_pokemon(values[0]).pokemon, "status_effect", None),
            "-cureteam": lambda values: (setattr(pokemon, "status_effect", None) for pokemon in
                                         self.get_player(values[0][:-1]).team),
            "-item": lambda values: setattr(self.get_sent_pokemon(values[0]).pokemon.info, "item",
                                            self.parsers["load_item"](values[1])),
            "-enditem": lambda values: setattr(self.get_sent_pokemon(values[0]).pokemon.info, "item", None),
            "-ability": lambda values: setattr(self.get_sent_pokemon(values[0]).pokemon.info, "ability",
                                               self.parsers["load_ability"](values[1]))
        }

    def is_fully_loaded(self) -> bool:
        return self.player is not None and self.opponent is not None

    def players(self):
        return self.player, self.opponent

    def get_player(self, name: str) -> Optional[Player]:
        if self.player is not None and name == self.player.username or name == "p1":
            return self.player
        if self.opponent is not None and name == self.opponent.username or name == "p2":
            return self.opponent

    def get_sent_pokemon(self, identifier: str) -> Optional[SentPokemon]:
        if ":" in identifier:
            identifier = identifier.split(":")[0]
        player = self.get_player(identifier[:-1])
        if player is not None:
            return player.sent.get(identifier[-1])

    def finish(self, winner: Optional[Player]):
        print(f"{winner} won the game !")

    @staticmethod
    def empty(parsers: Dict[str, Callable[[List[str]], None]]):
        return Battle(None, None, parsers)


class Room(Client):

    def __init__(self, room_id: str, title: str, users: List[str], parsers: Dict[str, Callable[[List[str]], None]],
                 battle: Optional[Battle] = None):
        super().__init__()
        self.room_id = room_id
        self.title = title
        self.users = users
        self.parsers = parsers
        self.battle = Battle.empty(parsers) if battle is None else battle

    def on_message_received(self, header: str, values: List[str]):
        print(f"Received {header} with {','.join(values)} in {self.room_id}")
        if self.battle is not None:
            self.battle.on_message_received(header, values)
