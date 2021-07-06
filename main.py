#!/usr/bin/python3

import logging
from pytz import timezone

from parsers.haaretz_parser import HaaretzParser
from parsers.israel_hayom_parser import IsraelHayomParser
from parsers.walla_parser import WallaParser
from loggers import setup_loggers

TIMEZONE = 'Israel'
LOCAL_TZ = timezone(TIMEZONE)
PARSER_CLASSES = [HaaretzParser, IsraelHayomParser, WallaParser]


def main():
    setup_loggers()
    logging.info('Starting script')

    logging.debug('Starting Parsers')
    parsers = [parser_class(LOCAL_TZ) for parser_class in PARSER_CLASSES]
    for parser in parsers:
        logging.info(f"Parsing {parser.get_source()}")
        parser.parse()
    
    logging.debug('Finished')


if __name__ == "__main__":
    main()
