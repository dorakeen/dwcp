import pathlib
from ruamel.yaml import YAML

# Configure YAML to preserve formatting
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

SETNAME_TO_YAMLNAME = {
    "base": "base-set.yaml",
    "intrigue": "intrigue.yaml",
    "promos": "promos.yaml",
    "seaside": "seaside.yaml",
    "alchemy": "alchemy.yaml",
    "prosperity": "prosperity.yaml",
    "cornucopia": "cornucopia.yaml",
    "hinterlands": "hinterlands.yaml",
    "dark_ages": "dark-ages.yaml",
    "guilds": "guilds.yaml",
    "adventures": "adventures.yaml",
    "empires": "empires.yaml",
    "base-update": "base-set-update.yaml",
    "intrigue-update": "intrigue-update.yaml",
    "nocturne": "nocturne.yaml",
    "renaissance": "renaissance.yaml",
    "menagerie": "menagerie.yaml",
    "allies": "allies.yaml",
    "seaside-update": "seaside-update.yaml",
    "prosperity-update": "prosperity-update.yaml",
    "hinterlands-update": "hinterlands-update.yaml",
    "plunder": "plunder.yaml",
    "cornucopia-guilds-update": "cornucopia-guilds-update.yaml"
    #"rising-sun": "rising-sun.yaml"
}

# ===============================================================================
# Create cards attributes dictionary
# ===============================================================================
def set_default_card_attibutes() :
    '''
    Sets default card attributes for a card
    '''

    card_attibutes = {
                      'isAction': False,
                      'isActionSupplier': False,
                      'isArtifactSupplier': False,
                      'isAttack': False,
                      'isBuySupplier': False,
                      'isDoom': False,
                      'isDrawer': False,
                      'isDuration': False,
                      'isFate': False,
                      'isLiaison': False,
                      'isMultiDrawer': False,
                      'isNight': False,
                      'isOmen': False,
                      'isReaction': False,
                      'isReserve': False,
                      'isTrashing': False,
                      'isTraveller': False,
                      'isTreasure': False,
                      'isVictory': False,
                      'isTerminal': True
    }

    return card_attibutes


def add_pick_times_to_cards(file_path, times):
    try:
        # Read the existing content
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file)
        
        # Add pickTimes if not present
        if 'cards' in data:
            modified = False
            for card in data['cards']:
                print(f"CARD: {card}")

                if 'pickTimes' not in card:
                    card['pickTimes'] = times
                    modified = True

                if 'toPick' not in card:
                    card['toPick'] = True
                    modified = True
            
            # Only write if changes were made
            if modified:
                with open(file_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data, file)
                print(f"Successfully updated {file_path}")

            else:
                print("No changes needed - pickTimes already exists")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":

    times = len(SETNAME_TO_YAMLNAME)
    for setname, yamlname in SETNAME_TO_YAMLNAME.items():
        print(f"\n[{setname}][{yamlname}]")

        set_filepath = pathlib.Path.cwd() / "sets" / yamlname
        #set_filepath = pathlib.Path('sets/base-set.yaml')

        add_pick_times_to_cards(set_filepath, times)
        times -= 1
