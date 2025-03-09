#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
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
# Date: 2021-09-01
#
# Version: 0.1
#
# Usage: python3 dwcp.py
#
# Requirements:
#   - Python 3.6 or higher
#   - PyYAML
#   - Rich
#
# TODO:
#   - Selection of one Favor card (from Allies) when one or more Liaison cards are selected
#   - Save the picked cards to the respective yaml files
#   - Save the picked cards to a database
#   - Selection of one Prophecy card (from Rising Sun) when one or more Omen cards are selected
#   - Add support for specifying the number of kingdom and landscape cards to select
#   - Add support for specifying the card sets to include in the selection
#   - Add support for specifying the card attributes to weight the selection
#   - Add support for specifying the card attributes to exclude from the selection
#   - Save the selection to a file
#   - Save the selection to a database
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
import yaml

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
# CARDS 
# This is needed to iterate over cards types
# This is also used as master list of all setnames themselves 
SETNAME_TO_YAMLNAME = {
    "base": "base-set.yaml",
    "base-update": "base-set-update.yaml",
    "intrigue": "intrigue.yaml",
    "intrigue-update": "intrigue-update.yaml",
    "seaside": "seaside.yaml",
    "seaside-update": "seaside-update.yaml",
    "alchemy": "alchemy.yaml",
    "prosperity": "prosperity.yaml",
    "prosperity-update": "prosperity-update.yaml",
    "cornucopia": "cornucopia.yaml",
    "hinterlands": "hinterlands.yaml",
    "hinterlands-update": "hinterlands-update.yaml",
    "dark_ages": "dark-ages.yaml",
    "guilds": "guilds.yaml",
    "cornucopia-guilds-update": "cornucopia-guilds-update.yaml",
    "adventures": "adventures.yaml",
    "empires": "empires.yaml",
    "nocturne": "nocturne.yaml",
    "renaissance": "renaissance.yaml",
    "menagerie": "menagerie.yaml",
    "allies": "allies.yaml",
    "plunder": "plunder.yaml",
    #"rising-sun": "rising-sun.yaml",
    "promos": "promos.yaml"
}
# #
#

#
# LANDSCAPES
# This is needed to iterate over landscape types
LANDSCAPE_NAMES_TO_NAME = {
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
# Create master randomizer piles
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

    randpiles = {
        "kingdoms": [],
        "landscapes": []
    }

    log.debug(f" ==== create_randomizer_piles({l_args})")

    card_attibutes = set_default_card_attibutes()
    for setname, yamlname in SETNAME_TO_YAMLNAME.items():
        log.debug(f" [{setname}][{yamlname}]")

        set_filepath = pathlib.Path.cwd() / "sets" / yamlname
        with open(set_filepath, 'r', encoding="utf-8") as file:
            dSet = yaml.safe_load(file)
            # log.debug(f" {dSet}")

        # Iterate over each kingdom card, and copy into randpiles while adding key/value for the set name itself
        for kcard in dSet["cards"]:
            kcard = card_attibutes | kcard
            kcard["set"] = setname
            # log.debug(f" {kcard}")
            if kcard["toPick"] :
                randpiles["kingdoms"].append(kcard)
            else :
                log.debug(f"\t{kcard['name']} not to be picked")

        # Iterate over each landscape card type, and copy into randpiles while adding key/value
        # for the set name itself, and the key/value of the landscape type
        for name_p, name_s in LANDSCAPE_NAMES_TO_NAME.items():
            if name_p in dSet:
                for landscape in dSet[name_p]:
                    landscape["set"] = setname
                    landscape["type"] = name_s
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
        kingdom_cards = random.sample(randpiles["kingdoms"], min(num_kingdom, len(randpiles["kingdoms"])))
        picked["kingdoms"].extend(kingdom_cards)
        # Remove picked cards from randomizer pile
        for card in kingdom_cards:
            randpiles["kingdoms"].remove(card)

    # Pick landscape cards 
    if randpiles["landscapes"] and num_landscape > 0:
        landscape_cards = random.sample(randpiles["landscapes"], min(num_landscape, len(randpiles["landscapes"])))
        picked["landscapes"].extend(landscape_cards)
        # Remove picked cards from randomizer pile
        for card in landscape_cards:
            randpiles["landscapes"].remove(card)

    return picked



# ===============================================================================
# dwcp(l_args)
# =============================================================================== 
def print_result(selection) :
    """
    Print the selected cards
    """
    
    console.print("")
    console.print("               ─━═ Kingdom Cards ═━─        ", style='bold blue1')
    n = 1
    log.info("Selected Kingdom Cards:")
    for kcard in selection["kingdoms"]:
        # Set color. For multi-types, the first chosen here is the priority color
        if kcard.get('isTreasure'):
            color = "yellow"
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

        log.info(f"\t{kcard['name']}\t({kcard['set']})")
        # <3 and <20 for spacing. Num has to be combined with . old fashioned way for this to work
        console.print(f"{str(n) + '.' : <3} [{color}]{kcard['name'] : <27}[/{color}] ({kcard['set'].title()})")
        n += 1


    console.print("")
    console.print("             ─━═ Landscapes Cards ═━─        ", style='bold blue1')
    n = 1
    log.info("Selectedionndscape Cards:") 
    for landscape in selection["landscapes"]:
        if landscape['type'] == 'event': 
            color = "bright_black"
        elif landscape['type'] == 'landmark': 
            color = "green"
        elif landscape['type'] == 'prophecy': 
            color = "deep_sky_blue3"
        elif landscape['type'] == 'project': 
            color = "red"
        elif landscape['type'] == 'way': 
            color = "cyan"
        elif landscape['type'] == 'trait': 
            color = "magenta"
        else: 
            color = "white"

        log.info(f"\t{landscape['name']}\t({landscape['set']}) - {landscape['type']}")
        # <3 and <27 for spacing. Num has to be combined with . old fashioned way for this to work
        console.print(f"{str(n) + '.' : <3} [{color}]{landscape['name'] : <27}[/{color}] ({landscape['set'].title()})\t- ({landscape['type'].title()})")
        n += 1

    console.print("")
    

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
    title = r'''
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
