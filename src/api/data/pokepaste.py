from api.data.pokemon import Gender, Nature


def normalize_name(name):
    return name \
        .replace(" ", "") \
        .replace("-", "") \
        .replace(".", "") \
        .replace("\'", "") \
        .replace("%", "") \
        .replace("*", "") \
        .replace(":", "") \
        .strip() \
        .lower() \
        .encode('ascii', 'ignore') \
        .decode('utf-8')


def load(pkmn_export_string, load_species, load_item, load_ability, load_nature, load_move):
    def get_species(s):
        if '(' in s and ')' in s:
            species = s[s.find("(") + 1:s.find(")")]
            return species
        return None

    pkmn_dict = {
        "nickname": None,
        "species": None,
        "level": 100,
        "gender": None,
        "item": None,
        "ability": None,
        "moves": [],
        "nature": Nature.NEUTRAL,
        "evs": {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0,
        },
    }
    pkmn_info = pkmn_export_string.split('\n')
    name = pkmn_info[0].split('@')[0]
    if "(M)" in name:
        pkmn_dict["gender"] = Gender.MALE
        name = name.replace('(M)', '')
    if "(F)" in name:
        pkmn_dict["gender"] = Gender.FEMALE
        name = name.replace('(F)', '')
    species = get_species(name)
    if species:
        pkmn_dict["species"] = load_species(normalize_name(species))
        pkmn_dict["nickname"] = name.split('(')[0].strip()
    else:
        name = normalize_name(name.strip())
        pkmn_dict["species"] = load_species(name)
    if '@' in pkmn_info[0]:
        pkmn_dict["item"] = load_item(normalize_name(pkmn_info[0].split('@')[1]))
    for line in map(str.strip, pkmn_info[1:]):
        if line.startswith('Ability: '):
            pkmn_dict["ability"] = load_ability(normalize_name(line.split('Ability: ')[-1]))
        elif line.startswith('Level: '):
            pkmn_dict["level"] = int(normalize_name(line.split('Level: ')[-1]))
        elif line.startswith('EVs: '):
            evs = line.split('EVs: ')[-1]
            for ev in evs.split('/'):
                ev = ev.strip()
                amount = normalize_name(ev.split(' ')[0])
                stat = normalize_name(ev.split(' ')[1])
                pkmn_dict['evs'][stat] = amount
        elif line.endswith('Nature'):
            pkmn_dict["nature"] = load_nature(normalize_name(line.split('Nature')[0]))
        elif line.startswith('-'):
            pkmn_dict["moves"].append(load_move(normalize_name(line[1:])))
    return pkmn_dict
