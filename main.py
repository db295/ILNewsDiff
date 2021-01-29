#!/usr/bin/python3

import logging
import os
import sys

from pytz import timezone

from HaaretzParser import HaaretzParser

TIMEZONE = 'Israel'
LOCAL_TZ = timezone(TIMEZONE)


if 'LOG_FOLDER' in os.environ:
    LOG_FOLDER = os.environ['LOG_FOLDER']
else:
    LOG_FOLDER = ''

PHANTOMJS_PATH = os.environ['PHANTOMJS_PATH']



def main():
    # logging
    logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_FOLDER + 'titlediff.log',
                                                      encoding='utf-8', mode='a+'),
                                  logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s %(name)13s %(levelname)8s: ' +
                               '%(message)s',
                        level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.info('Starting script')

    # consumer_key = os.environ['NYT_TWITTER_CONSUMER_KEY']
    # consumer_secret = os.environ['NYT_TWITTER_CONSUMER_SECRET']
    # access_token = os.environ['NYT_TWITTER_ACCESS_TOKEN']
    # access_token_secret = os.environ['NYT_TWITTER_ACCESS_TOKEN_SECRET']
    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    # auth.secure = True
    # auth.set_access_token(access_token, access_token_secret)
    # twitter_api = tweepy.API(auth)
    # logging.debug('Twitter API configured')

    try:
        logging.debug('Starting Parsers')
        parsers = [HaaretzParser(None, LOCAL_TZ, PHANTOMJS_PATH)]
        for parser in parsers:
            parser.parse()
        logging.debug('Finished')
    except:
        logging.exception('Parser')

    logging.info('Finished script')


if __name__ == "__main__":
    main()
