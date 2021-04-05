from enum import Enum
from typing import List

from api import PokemonInfo


class StatusEffect(Enum):
    BURN = "brn"
    FREEZE = "frz"
    POISON = "tox"
    SLEEP = "slp"


class VolatileStatus(Enum):
    CONFUSION = "confusion"
    DISABLE = "disable"
    SUBSTITUTE = "substitute"
    TAUNT = "taunt"
    TRAPPED = "trapped"
    UNKNOWN = "unknown"


class Pokemon:

    def __init__(self, info: PokemonInfo, health: float = 1, status_effect: StatusEffect = None):
        self.info = info
        self.health = health
        self.status_effect = status_effect


class SentPokemon:

    def __init__(self, pokemon: Pokemon, volatile_status: VolatileStatus = None, dynamaxed: bool = False):
        self.pokemon = pokemon
        self.volatile_status = volatile_status
        self.dynamaxed = False


class Player:

    def __init__(self, user: str, team: List[Pokemon], sent: SentPokemon = None):
        self.user = user
        self.team = team
        self.sent = sent
