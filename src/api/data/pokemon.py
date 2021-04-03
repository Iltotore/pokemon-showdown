import os
import re
from enum import Enum, IntEnum
from typing import Tuple, List, Dict, Any


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
    WATER, \
    UNKNOWN = range(19)


class Stat(Enum):
    ATTACK = "Atk"
    DEFENSE = "Def"
    SPECIAL_ATTACK = "SpA"
    SPECIAL_DEFENSE = "SpD"
    SPEED = "Spe"


class Flavor(IntEnum):
    SPICY, \
    DRY, \
    SWEET, \
    BITTER, \
    SOUR = range(5)


class Nature(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, raised_stat, lowed_stat, like, dislike):
        self.raised_stat = raised_stat
        self.lowed_stat = lowed_stat
        self.like = like
        self.dislike = dislike

    BOLD = Stat.DEFENSE, Stat.ATTACK, Flavor.SOUR, Flavor.SPICY
    BRAVE = Stat.ATTACK, Stat.SPEED, Flavor.SPICY, Flavor.SWEET
    CALM = Stat.SPECIAL_DEFENSE, Stat.ATTACK, Flavor.BITTER, Flavor.SPICY
    QUIET = Stat.SPECIAL_ATTACK, Stat.SPEED, Flavor.DRY, Flavor.SWEET
    MILD = Stat.SPECIAL_ATTACK, Stat.DEFENSE, Flavor.DRY, Flavor.SOUR
    RASH = Stat.SPECIAL_ATTACK, Stat.SPECIAL_DEFENSE, Flavor.DRY, Flavor.BITTER
    GENTLE = Stat.SPECIAL_DEFENSE, Stat.DEFENSE, Flavor.BITTER, Flavor.SOUR
    JOLLY = Stat.SPEED, Stat.SPECIAL_ATTACK, Flavor.SWEET, Flavor.DRY
    LAX = Stat.DEFENSE, Stat.SPECIAL_DEFENSE, Flavor.SOUR, Flavor.BITTER
    IMPISH = Stat.DEFENSE, Stat.SPECIAL_ATTACK, Flavor.SOUR, Flavor.DRY
    SASSY = Stat.SPECIAL_DEFENSE, Stat.SPEED, Flavor.BITTER, Flavor.SWEET
    NAUGHTY = Stat.ATTACK, Stat.SPECIAL_DEFENSE, Flavor.SPICY, Flavor.BITTER
    MODEST = Stat.SPECIAL_ATTACK, Stat.ATTACK, Flavor.DRY, Flavor.SPICY
    NAIVE = Stat.SPEED, Stat.SPECIAL_DEFENSE, Flavor.SWEET, Flavor.BITTER
    HASTY = Stat.DEFENSE, Stat.SPEED, Flavor.SWEET, Flavor.SOUR
    CAREFUL = Stat.SPECIAL_DEFENSE, Stat.SPECIAL_ATTACK, Flavor.BITTER, Flavor.DRY
    RELAXED = Stat.DEFENSE, Stat.SPEED, Flavor.SOUR, Flavor.SWEET
    ADAMANT = Stat.ATTACK, Stat.SPECIAL_ATTACK, Flavor.SPICY, Flavor.DRY
    LONELY = Stat.ATTACK, Stat.DEFENSE, Flavor.SPICY, Flavor.SOUR
    TIMID = Stat.SPEED, Stat.ATTACK, Flavor.SWEET, Flavor.SPICY
    NEUTRAL = None, None, None, None


class MoveType(IntEnum):
    PHYSICAL, SPECIAL, STATUS = range(3)


class Gender(Enum):
    MALE, FEMALE = "M", "F"


class NamedInfo:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.__dict__


def parse_named_info(name: str, loaded_info, default: Any = lambda name: None):
    for info in loaded_info:
        if info.name == name:
            return loaded_info
    return default(name)


class MoveInfo:

    def __init__(self, name):
        self.name = name


class LoadedMoveInfo(MoveInfo):

    def __init__(self, name: str, pokemon_type: Type, move_type: MoveType, description: str, pp: int,
                 base_power: int = 0,
                 accuracy: int = 100,
                 priority: int = 0):
        super().__init__(name)
        self.pokemon_type = pokemon_type
        self.move_type = move_type
        self.description = description
        self.pp = pp
        self.base_power = base_power
        self.accuracy = accuracy
        self.priority = priority


class Ability(NamedInfo):

    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description


def unknown_ability(name: str):
    return Ability(name, "???")


class Species(NamedInfo):

    def __init__(self, name: str, types: Tuple[Type], abilities: Tuple[Ability], moves: List[MoveInfo]):
        super().__init__(name)
        self.types = types
        self.abilities = abilities
        self.moves = moves


def unknown_species(name: str):
    return Species(name, (Type.UNKNOWN,), (), [])


class Item(NamedInfo):

    def __init__(self, name: str, description: str):
        super().__init__(name)
        self.description = description


def unknown_item(name: str):
    return Item(name, "???")


def mk_string(d: Dict[str, int]):
    items = list(d.items())
    if len(items) == 0:
        return ""
    result = f"{items[0][1]} {items[0][0]}"
    for i in range(1, len(items)):
        k, v = items[i]
        result += f" / {v} {k}"
    return result


class PokemonInfo:

    def __init__(self, species: Species,
                 ability: Ability,
                 moves: Tuple[MoveInfo],
                 item: Item,
                 ivs: Dict[str, int] = {},
                 evs: Dict[str, int] = {},
                 gender: Gender = None,
                 nature: Nature = Nature.NEUTRAL,
                 level: int = 100,
                 shiny: bool = False,
                 nickname: str = None,
                 happiness: int = 255):
        self.species = species
        self.ability = ability
        self.moves = moves
        self.item = item
        self.ivs = ivs
        self.evs = evs
        self.gender = gender
        self.nature = nature
        self.level = level
        self.shiny = shiny
        self.nickname = nickname
        self.happiness = happiness

    def __str__(self):
        name = self.species.name if self.nickname is None else f"{self.nickname} ({self.species.name})"

        options = ""
        if 100 > self.level > 0:
            options += f"Level: {self.level}\n"
        if self.shiny:
            options += "Shiny: Yes\n"
        if self.nature != "Serious":
            options += f"{self.nature.name} Nature\n"
        if len(self.ivs) > 0:
            options += f"IVs: {mk_string(self.ivs)}\n"
        if len(self.evs) > 0:
            options += f"EVs: {mk_string(self.evs)}"

        moves = ""
        for move in self.moves:
            moves += f"- {move.name}\n"

        return f"""
{name} @ {self.item.name}
Ability: {self.ability.name}
{options}
{moves}
        """

    def format(self):
        species_and_name = f"{self.nickname}|{self.species.name}" if self.nickname is not None else f"{self.species.name}|"

        def named_join(it, sep: str = ","):
            return sep.join([named.name for named in it])

        def stat_format(stats: Dict[str, int], default: int):
            result = str(stats.get("hp", default))
            for stat in ["atk", "def", "spa", "spd", "spe"]:
                result += f",{stats.get(stat, default)}"
            return result

        evs = stat_format(self.evs, 0)  # TODO Let's go support
        ivs = stat_format(self.ivs, 31)  # TODO Gen 1-2 support

        return f"{species_and_name}|{self.item.name}|{self.ability.name}|{named_join(self.moves)}|{self.nature.name}|{evs}|{self.gender.name if self.gender is not None else ''}|{ivs}|{'s' if self.shiny else ''}|{self.level}|{self.happiness},,"


def parse_pokemon(paste: str, load_species, load_items,
                  load_ability, load_nature, load_move):
    from api.data import pokepaste

    data = pokepaste.load(paste, load_species, load_items, load_ability, load_nature, load_move)

    data["evs"] = {k: v for k, v in data.get("evs", {}).items() if v}

    return PokemonInfo(**data)


class TeamContainer:

    def __init__(self, root: str, load_species, load_item, load_ability, load_nature, load_move):
        self.root = root
        self.load_species = load_species
        self.load_item = load_item
        self.load_ability = load_ability
        self.load_nature = load_nature
        self.load_move = load_move

        self.team_dict = {}

    def __getitem__(self, item):
        current_dir = self.team_dict
        for directory in item.split("/"):
            current_dir = current_dir[directory]
        return current_dir

    def all_teams(self):

        def get_dir(prefix, directory):
            results = []
            for k, v in directory.items():
                new_prefix = f"{prefix}/{k}" if len(prefix) > 0 else k
                if isinstance(v, Dict):
                    results += get_dir(new_prefix, v)
                else:
                    results.append((new_prefix, v))
            return results

        return get_dir("", self.team_dict)

    async def load_teams(self):
        if os.path.isfile(self.root):
            raise ValueError("root should be a directory")
        if not os.path.exists(self.root):
            os.mkdir(self.root)

        def load_subdir(root, directory):
            for file_name in os.listdir(directory):
                file = f"{directory}/{file_name}"
                if os.path.isdir(file):
                    load_subdir(root, file)
                else:
                    path = re.split(r"[/\\]", os.path.relpath(file, root))[:-1]
                    if not file_name.endswith(".pkmn"):
                        continue
                    name = file_name[:-5].replace("_", " ")

                    with open(file) as content:
                        lines = content.read()
                        raw_pokemons = lines.split("\n\n")

                        team = [parse_pokemon(paste, self.load_species,
                                              self.load_item,
                                              self.load_ability,
                                              self.load_nature,
                                              self.load_move) for paste in raw_pokemons]

                        folder = self.team_dict
                        for subfolder in path:
                            if subfolder not in folder:
                                child = {}
                                folder[subfolder] = child
                            folder = child
                        folder[name] = team

        load_subdir(self.root, self.root)


if __name__ == '__main__':
    import asyncio, time

    t = time.time()
    team_container = TeamContainer("../../teams",
                                   lambda name: parse_named_info(name, [], unknown_species),
                                   lambda name: parse_named_info(name, [], unknown_item),
                                   lambda name: parse_named_info(name, [], unknown_ability),
                                   lambda name: Nature[name.upper()],
                                   lambda name: parse_named_info(name, [], lambda n: MoveInfo(n)))

    asyncio.run(team_container.load_teams())
    for key, team in team_container.all_teams():
        for pkmn in team:
            print(pkmn)
            print(pkmn.format())

    print((time.time() - t) * 1000, "ms")
