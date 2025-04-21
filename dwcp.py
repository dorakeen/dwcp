# ===============================================================================
# Title: Dominion Weighted Card Picker
#
# Description:
#   This script will randomly select 10 kingdom cards and 0-2 landscape cards
#   from the Dominion card sets. The selection is weighted based on the
#   attributes of the cards.
#
#   The script will output the selected cards to the console.
#
#
# Author: dorakeen
#
# Date: 2025-03-01
#
# Version: 1.0
#
# Usage: python3 dwcp.py
#
# Requirements:
#   - Python 3.6 or higher
#   - PyYAML
#   - Rich
#
# TODO:
#   - Print the number of possible set selections
#   - Save the picked cards to the respective yaml files
#   - Selection max number of kingdom set cards
#   - Save the picked cards to a database
#   - Add support for specifying the number of kingdom and landscape cards to select
#   - Add support for specifying the card sets to include in the selection
#   - Add support for specifying the card attributes to weight the selection
#   - Add support for specifying the card attributes to exclude from the selection
#
# ===============================================================================
# 

# globals imports
import argparse
import logging
import logging.handlers
import pathlib
import random
import os
import sys
#import yaml
from ruamel.yaml import YAML

from rich.console import Console

# third-party libraries

# local imports

#
# LOGS SETTINGS
LOG_FILE = os.path.realpath(__file__) + '.log'
LOG_FILE_MAX_SIZE_KB = 5120
LOG_FILE_GENERATIONS = 5
LOG_FORMAT = '%(asctime)s -%(levelname)s- %(funcName)s:%(lineno)d - %(message)s'
LOG_LEVEL = logging.WARNING
log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)
FORMATTER = logging.Formatter(LOG_FORMAT)
SH = logging.StreamHandler()
SH.setFormatter(FORMATTER)
SH.setLevel(logging.DEBUG)
log.addHandler(SH)
# #
#

#
# Global vars

# Global variable to hold the card sets
dSet = 0
yaml = YAML()
    

# #
#

#
# CARDS 
# This is needed to iterate over cards types
# This is also used as master list of all setnames themselves 
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
# #
#

#
# LANDSCAPES
# This is needed to iterate over landscape types
LANDSCAPE_NAMES_TO_NAME = {
    "allies": "ally",
    "events": "event",
    "landmarks": "landmark",
    "prophecies": "prophecy",
    "projects": "project",
    "traits": "trait",
    "ways": "way"
}
# #
#

# ===============================================================================
# Create cards attributes dictionary
# ===============================================================================
def set_default_card_attibutes() :
    '''
    Sets default card attributes for a card
    '''

    card_attibutes = {
                      'pickTimes': 0,
                      'toPick': True,
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

# ===============================================================================
# Create landscapes attributes dictionary
# ===============================================================================
def set_default_landscape_attibutes() :
    '''
    Sets default landscape attributes for a landscape
    '''

    landscape_attibutes = {
                      'pickTimes': 0,
                      'toPick': True,
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

    return landscape_attibutes

# ===============================================================================
# Create master randomizer piles
# ===============================================================================
def create_randomizer_piles(l_args):
    '''
    Create Randomizer Piles (one for Kingdom, one for Landscape)
    kingdoms:
        [list of cards as dicts] - card has additional key/value of set
    landscapes:
        [list of landscapes as dicts] - card has additional key/value of set, and additional key/value of the type of landscape

    This list will be modified/deleted to track what cards were taken. Those cards will be "moved" to pickedpiles.
    '''

    global dSet

    randpiles = {
        "kingdoms": [],
        "landscapes": [],
        "allies": [],
        "prophecies": []
    }

    log.debug(f" ==== create_randomizer_piles({l_args})")

    card_attibutes = set_default_card_attibutes()
    for setname, yamlname in SETNAME_TO_YAMLNAME.items():
        log.debug(f" [{setname}][{yamlname}]")

        set_filepath = pathlib.Path.cwd() / "sets" / yamlname
        with open(set_filepath, 'r', encoding="utf-8") as file:
            dSet = yaml.load(file)
            # log.debug(f" {dSet}")

        log.debug(f"Set: {setname} - {len(dSet['cards'])} cards")
        # Iterate over each kingdom card, and copy into randpiles while adding key/value for the set name itself
        for kcard in dSet["cards"]:
            # LUK XXX kcard = card_attibutes | kcard
            kcard["set"] = setname
            # log.debug(f" {kcard}")
            if kcard["toPick"] :
                randpiles["kingdoms"].append(kcard)
            else :
                log.debug(f"\t{kcard['name']} not to be picked")

        # Iterate over each landscape card type, and copy into randpiles while adding key/value
        # for the set name itself, and the key/value of the landscape type
        log.debug('Landscape cards: ')
        for name_p, name_s in LANDSCAPE_NAMES_TO_NAME.items():
            if name_p in dSet:
                for landscape in dSet[name_p]:
                    landscape["set"] = setname
                    landscape["type"] = name_s

                    log.debug(f'\t{landscape}')
                    if landscape["type"] == 'ally' :
                        randpiles["allies"].append(landscape)
                    elif landscape["type"] == 'prophecy' :
                        randpiles["prophecies"].append(landscape)
                    else :
                        randpiles["landscapes"].append(landscape)

    return randpiles


# ===============================================================================
# pick_random_cards(randpiles, num_kingdom=10, num_landscape=0)
# ===============================================================================
def pick_random_cards(randpiles, num_kingdom=10, num_landscape=0):
    """
    Pick random cards from the randomizer piles
    Returns dict with selected kingdom and landscape cards
    """

    picked = {
        "kingdoms": [],
        "landscapes": []
    }

    # Pick kingdom cards
    if randpiles["kingdoms"]:
        # kingdom_cards = random.sample(randpiles["kingdoms"], min(num_kingdom, len(randpiles["kingdoms"])))

        weights = [float(1 / (card['pickTimes'] + 1)) for card in randpiles["kingdoms"]]
                
        log.debug(f"randpiles['kingdoms']: {len(randpiles['kingdoms'])}")
        console.print()
        console.print(f"Selecting {num_kingdom} kingdoms from a set of {len(randpiles['kingdoms'])} ...", style='bold blue1')
        console.print()

        for _ in  range(num_kingdom) :
            kc = random.choices(randpiles["kingdoms"], weights=weights, k=1)

            selected_idx = randpiles["kingdoms"].index(kc[0])
            print(f"PICK: Card ID {selected_idx:03} - {kc[0]['name']}\t ({kc[0]['set']}) \t[{kc[0]['pickTimes']}]")
            
            picked["kingdoms"].append(kc[0])

            # Remove picked cards from randomizer pile
            # randpiles["kingdoms"].remove(kc[0])
            randpiles["kingdoms"].pop(selected_idx)
            weights.pop(selected_idx)

        # Looking for Liaison/Omen cards in the picked kingdom cards
        ally_card = None
        prophecy_card = None
        for kcard in picked["kingdoms"]:

            kcard['pickTimes'] += 1

            if ally_card == None and kcard.get('isLiaison'):
                # Pick one Ally card from Allies
                ally_card = random.choice(randpiles["allies"])
                picked["landscapes"].append(ally_card)

            if prophecy_card == None and kcard.get('isOmen'):
                # Pick one Prophecy card from Prophecies
                prophecy_card = random.choice(randpiles["prophecies"])
                picked["landscapes"].append(prophecy_card)
                

    # Sort the picked kingdom cards by name
    picked["kingdoms"].sort(key=lambda x: x['name'])
    
    # Pick landscape cards 
    if randpiles["landscapes"] and num_landscape > 0:
        landscape_cards = random.sample(randpiles["landscapes"], min(num_landscape, len(randpiles["landscapes"])))
        picked["landscapes"].extend(landscape_cards)

        #for lcard in picked["landscapes"]:
            #lcard['pickTimes'] += 1

        # Remove picked cards from randomizer pile
        # for card in landscape_cards:
            # randpiles["landscapes"].remove(card)

    return picked



# ===============================================================================
# print_result(l_args)
# =============================================================================== 
def print_result(selection) :
    """
    Print the selected cards
    """
    
    console.print("")
    console.print("          ─━═ Kingdom Cards ═━─        ", style='bold blue1')
    n = 1
    sets_list = set()
    log.info("Selected Kingdom Cards:")
    for kcard in selection["kingdoms"]:
        # Set color. For multi-types, the first chosen here is the priority color
        if kcard.get('isTreasure'):
            color = "gold1"
        elif kcard.get('isAttack'): 
            color = "red"
        elif kcard.get('isReaction'): 
            color = "cyan"
        elif kcard.get('isVictory'): 
            color = "green"
        else: 
            color = "white"

        """
        # Manual exception: Harem now is known as Farm
        if kcard['name'] == 'Harem':
            kcard['name'] = 'Harem (Farm)'
        """

        sets_list.add(kcard['set'])
        
        log.info(f"\t{kcard['name']}\t({kcard['set']})")
        # <3 and <20 for spacing. Num has to be combined with . old fashioned way for this to work
        console.print(f"{str(n) + '.' : <3} [{color}]{kcard['name'] : <17}[/{color}] ({kcard['set'].title()})")
        n += 1

    # platinum / colony selection (15%)
    platcol = random.randint(1, 100)
    if platcol <= 15 :
        console.print("")
        console.print(f"Makes use of [gold1]Platinum[/gold1] and [green]Colonies[/green] ")


    # shelter selection (11%)
    platcol = random.randint(1, 100)
    if platcol <= 11 :
        console.print("")
        console.print(f"Makes use of [orange4]Shelters[/orange4] ")

    console.print("")
    console.print("        ─━═ Landscapes Cards ═━─        ", style='bold blue1')
    n = 1
    log.info("Selected Landscape Cards:") 
    for landscape in selection["landscapes"]:
        if landscape['type'] == 'ally': 
            color = "yellow"
        elif landscape['type'] == 'event': 
            color = "bright_black"
        elif landscape['type'] == 'landmark': 
            color = "green"
        elif landscape['type'] == 'prophecy': 
            color = "deep_sky_blue3"
        elif landscape['type'] == 'project': 
            color = "salmon1"
        elif landscape['type'] == 'way': 
            color = "cyan"
        elif landscape['type'] == 'trait': 
            color = "magenta"
        else: 
            color = "white"

        sets_list.add(landscape['set'])

        log.info(f"\t{landscape['name']}\t({landscape['set']}) - {landscape['type']}")
        # <3 and <17 for spacing. Num has to be combined with . old fashioned way for this to work
        console.print(f"{str(n) + '.' : <3} [{color}]{landscape['name'] : <17}[/{color}] ({landscape['set'].title()}) - ({landscape['type'].title()})")
        n += 1

    color = "white"
    sets_list = sorted(sets_list)  # Sort the set names alphabetically

    console.print("")
    console.print(f"        ─━═ {len(sets_list)} Sets Choosen ═━─        ", style='bold blue1')
    #console.print(f"[{color}]{', '.join(sets_list)}[/{color}] ") # one line list
    for s in sets_list :
        console.print(f"[{color}]{s.title()}[/{color}] ")

    console.print("")
    

# ===============================================================================
# save_picked_cards(selection)
# =============================================================================== 
def save_picked_cards(selection) :
    """
    Saves the picked cards to the respective yaml files.
    This is needed to select the weight probability.
    """
    global dSet
    
    #print(dSet)
    for kcard in selection["kingdoms"]:
        pass

    for landscape in selection["landscapes"]:
        pass


# ===============================================================================
# dwcp(l_args)
# ===============================================================================
def dwcp(l_args):
    """ starting point function """

    log.debug(f" ==== dwcp({l_args})")

    #
    # Evaluate given options

    randpiles = create_randomizer_piles(l_args)

    # Pick random cards (10 kingdom, 0/2 landscape)
    selected = pick_random_cards(randpiles, num_kingdom=10, num_landscape=random.randrange(3))
    
    print_result(selected)

    save_picked_cards(selected)

    return selected


# ===============================================================================
# logging handler
# ===============================================================================
def setup_file_log(l_args):
    """ Setting up Logging """

    if l_args.log_size is None:
        log_max_bytes = LOG_FILE_MAX_SIZE_KB * 1024
    else:
        log_max_bytes = l_args.log_size * 1024

    if l_args.log_generations is None:
        backup_count = LOG_FILE_GENERATIONS
    else:
        backup_count = l_args.log_generations

    fh = logging.handlers.RotatingFileHandler(l_args.log_file,
                                              maxBytes=log_max_bytes,
                                              backupCount=backup_count)
    fh.setLevel(l_args.log_level)
    fh.setFormatter(FORMATTER)
    log.addHandler(fh)


# ===============================================================================
# argument parser
# ===============================================================================
def get_argparse():
    """ Setting Up Argument Parser """

    l_parser = argparse.ArgumentParser()

    #
    # mandatory arguments
    # l_parser.add_argument('-if', '--infile', required=True, help='input file. Required')

    #
    # optional arguments
    l_parser.add_argument('-l', '--log-file', default=LOG_FILE,
                        help='Path to python-script logfile. Default is path to script + .log')
    l_parser.add_argument('-ll', '--log-level',
                        default='WARNING',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
                        help='Logfile Loglevel.  Default = INFO')
    l_parser.add_argument('-lms', '--log-size',
                        default=LOG_FILE_MAX_SIZE_KB,
                        type=int,
                        nargs='?',
                        help='Logfile max. size in kB. Default = 5120 kB')
    l_parser.add_argument('-lgen', '--log-generations',
                        default=LOG_FILE_GENERATIONS,
                        type=int,
                        nargs='?',
                        help='Logfile max. generations. Default = 5')

    return l_parser

# ===============================================================================
#  main entry point
# ===============================================================================
if __name__ == '__main__':

    console = Console()

    title = r'''
___________       _________________ 
___  __ \_ |     / /_  ____/__  __ \
__  / / /_ | /| / /_  /    __  /_/ /
_  /_/ /__ |/ |/ / / /___  _  ____/ 
/_____/ ____/|__/  \____/  /_/
    '''
    title2 = r'''
.----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. |
| |  ________    | || | _____  _____ | || |     ______   | || |   ______     | |
| | |_   ___ `.  | || ||_   _||_   _|| || |   .' ___  |  | || |  |_   __ \   | |
| |   | |   `. \ | || |  | | /\ | |  | || |  / .'   \_|  | || |    | |__) |  | |
| |   | |    | | | || |  | |/  \| |  | || |  | |         | || |    |  ___/   | |
| |  _| |___.' / | || |  |   /\   |  | || |  \ `.___.'\  | || |   _| |_      | |
| | |________.'  | || |  |__/  \__|  | || |   `._____.'  | || |  |_____|     | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'
 '''
    subtitle = r'''by dorakeen'''
        
    console.print(title, style='bold', highlight=False)
    console.print(subtitle)
    
    try:
        parser = get_argparse()
        args = parser.parse_args()

        setup_file_log(args)
        log.setLevel(args.log_level)

        log.info("\n================= Start Dominion Weighted Card Picker =================\n")
        log.debug(f"Args: {args}")


    except Exception as e:
        # Output error, and return with an error code
        print(f'Setup Log not possible !! {e} !!')
        sys.exit(2)

    dwcp(args)

    log.info("\n================= Stop Dominion Weighted Card Picker =================\n")
