from enum import Enum
from typing import List, Optional, Dict

from api.data.pokemon import PokemonInfo, Gender, unknown_ability, Stat


class StatusEffect(Enum):
    BURN = "brn"
    FREEZE = "frz"
    PARALYSIS = "par"
    POISON = "tox"
    SLEEP = "slp"


class VolatileStatus(Enum):
    CONFUSION = "confusion"
    DISABLE = "disable"
    SUBSTITUTE = "substitute"
    TAUNT = "taunt"
    TRAPPED = "trapped"
    UNKNOWN = "unknown"


class Weather(Enum):
    INTENSE_SUN = "DesolateLand",
    SUN = "SunnyDay",
    RAIN = "RainDance",
    HEAVY_RAIN = "PrimordialSea",
    HAIL = "Hail",
    SANDSTORM = "Sandstorm",
    STRONG_WINDS = "DeltaStream"


class Pokemon:

    def __init__(self, identifier: str, info: PokemonInfo, health: int = 100, max_health=100,
                 status_effect: Optional[StatusEffect] = None):
        self.identifier = identifier
        self.info = info
        self.health = health
        self.max_health = max_health
        self.status_effect = status_effect

    def faint(self):
        self.health = 0

    def is_fainted(self):
        return self.health <= 0

    @staticmethod
    def deserialize(identifier: str, item: str, load_species, load_item):
        details = identifier.split(", ")
        # noinspection PyTypeChecker
        info_kwargs = {
            "species": load_species(details[0]),
            "ability": unknown_ability("Unknown"),
            "moves": (),
            "item": load_item(item)
        }
        for value in details[1:]:
            if value.startswith("L"):
                info_kwargs["level"] = int(value[1:])
            if value == "M" or value == "F":
                info_kwargs["gender"] = Gender.MALE if value == "M" else Gender.FEMALE

        return Pokemon(identifier, PokemonInfo(**info_kwargs))


class SentPokemon:

    def __init__(self, pokemon: Pokemon, stats_changes: Dict[Stat, float] = {},
                 volatile_status: Optional[VolatileStatus] = None, dynamaxed: bool = False):
        self.pokemon = pokemon
        self.stats_changes = stats_changes
        self.volatile_status = volatile_status
        self.dynamaxed = dynamaxed

    def faint(self):
        self.pokemon.faint()  # Future animation


class Player:

    def __init__(self, username: str, trainer: int, team: List[Pokemon] = [], rating: Optional[int] = None,
                 sent: Dict[str, SentPokemon] = {}):
        self.username = username
        self.trainer = trainer
        self.team = team
        self.rating = rating
        self.sent = sent

    @staticmethod
    def deserialize(username: str, trainer: str, rating: str):
        return Player(username, int(trainer), rating=None if rating is None else int(rating))
