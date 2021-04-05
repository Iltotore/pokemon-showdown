from typing import List

from battle.entity import Player


class State:
    pass


PREVIEW, BATTLING = State(), State()


class End(State):

    def __init__(self, winner: Player):
        self.winner = winner


class Battle:

    def __init__(self, player: Player, opponent: Player, state: State = PREVIEW):
        self.player = player
        self.opponent = opponent
        self.state = state


class Room:

    def __init__(self, room_id: str, title: str, users: List[str], battle: Battle = None):
        self.room_id = room_id
        self.title = title
        self.users = users
        self.battle = battle
