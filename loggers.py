import logging
import os
import sys

if 'LOG_FOLDER' in os.environ:
    LOG_FOLDER = os.environ['LOG_FOLDER']
else:
    LOG_FOLDER = ''


def setup_loggers():
    # Add Handlers 
    logging_filehandler = logging.FileHandler(filename=os.path.join(LOG_FOLDER, 'titlediff.log'), encoding='utf-8', mode='a+')
    handlers = [logging_filehandler, logging.StreamHandler(sys.stdout)]
    logging.basicConfig(handlers=handlers,
                        format='%(asctime)s %(name)13s %(levelname)8s: %(message)s',
                        level=logging.DEBUG)

    # Handle some loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)
    logging.getLogger("chardet").setLevel(logging.WARNING)
    logging.getLogger("tweepy").setLevel(logging.WARNING)
    logging.getLogger("oauthlib").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
