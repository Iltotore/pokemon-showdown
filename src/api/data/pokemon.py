from enum import Enum
from typing import Tuple, List


class Type(Enum):
    BUG, \
    DARK, \
    DRAGON, \
    ELECTRIC, \
    FAIRY, \
    FIGHTING, \
    FIRE, \
    FLYING, \
    GHOST, \
    GRASS, \
    GROUND, \
    ICE, \
    NORMAL, \
    POISON, \
    PSYCHIC, \
    ROCK, \
    STEEL, \
    WATER = range(18)


class MoveType(Enum):
    PHYSICAL, SPECIAL, STATUS = range(2)


class Move:

    def __init__(self, name: str, pokemon_type: Type, move_type: MoveType, description: str, base_power: int = 0,
                 priority: int = 0):
        self.name = name
        self.pokemon_type = pokemon_type
        self.move_type = move_type
        self.description = description
        self.base_power = base_power
        self.priority = priority


class Species:

    def __init__(self, name: str, abilities: List[Tuple[str]], moves: List[Move]):
        self.name = name
        self.abilities = abilities
        self.moves = moves
