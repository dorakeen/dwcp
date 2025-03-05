#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
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

    for setname, yamlname in SETNAME_TO_YAMLNAME.items():
        log.debug(f" [{setname}][{yamlname}]")

        set_filepath = pathlib.Path.cwd() / "sets" / yamlname
        with open(set_filepath, 'r', encoding="utf-8") as file:
            dSet = yaml.safe_load(file)

        # Iterate over each kingdom card, and copy into randpiles while adding key/value for the set name itself
        for kcard in dSet["cards"]:
            kcard["set"] = setname
            #log.debug(f" [{kcard}]")
            randpiles["kingdoms"].append(kcard)

        # Iterate over each landscape card type, and copy into randpiles while adding key/value
        # for the set name itself, and the key/value of the landscape type
        for name_p, name_s in LANDSCAPE_NAMES_TO_NAME.items():
            if name_p in dSet:
                for landscape in dSet[name_p]:
                    landscape["set"] = setname
                    landscape["type"] = name_s
                    randpiles["landscapes"].append(landscape)

    log.debug(f" [{randpiles}]")
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
def dwcp(l_args):
    """ starting point function """

    log.debug(f" ==== dwcp({l_args})")

    #
    # Evaluate given options

    randpiles = create_randomizer_piles(l_args)

    # Pick random cards (10 kingdom, 0/2 landscape)
    selected = pick_random_cards(randpiles, num_kingdom=10, num_landscape=random.randrange(3))
    
    # Log results
    log.info("Selected Kingdom Cards:")
    for card in selected["kingdoms"]:
        log.info(f"\t{card['name']}\t({card['set']})")
    
    log.info("Selected Landscape Cards:") 
    for card in selected["landscapes"]:
        log.info(f"\t{card['name']}\t({card['set']}) - {card['type']}")

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
                        default='INFO',
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

    try:
        parser = get_argparse()
        args = parser.parse_args()

        setup_file_log(args)
        log.setLevel(args.log_level)

        log.info(" ================= Start Dominion Weighted Card Picker =================")
        log.debug(f"Args: {args}")


    except Exception as e:
        # Output error, and return with an error code
        print(f'Setup Log not possible !! {e} !!')
        sys.exit(2)

    dwcp(args)

    log.info(" ================= Stop Dominion Weighted Card Picker =================")
