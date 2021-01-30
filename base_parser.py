import logging
import os
import sys
import time

import bleach
import requests

from data_provider import DataProvider
from image_diff_generator import generate_image_diff

if 'TESTING' in os.environ:
    if os.environ['TESTING'] == 'False':
        TESTING = False
    else:
        TESTING = True
else:
    TESTING = True

MAX_RETRIES = 10
RETRY_DELAY = 3


class BaseParser():
    def __init__(self, api, phantomjs_path):
        self.api = api
        self.phantomjs_path = phantomjs_path
        self.data_provider = DataProvider()

    def parse(self):
        raise NotImplemented

    def entry_to_dict(self, article):
        raise NotImplemented() 

    def test_twitter(self):
        print(self.api.rate_limit_status())
        print(self.api.me().name)

    def media_upload(self, filename):
        if TESTING:
            return 1
        try:
            response = self.api.media_upload(filename)
        except:
            print(sys.exc_info()[0])
            logging.exception('Media upload')
            raise
        return response.media_id_string

    def tweet_with_media(self, text, images, reply_to=None):
        logging.debug(f"Tweeting {text} with {images} in reply to {reply_to}")
        if TESTING:
            print(text, images, reply_to)
            return True
        try:
            if reply_to is not None:
                tweet_id = self.api.update_status(
                    status=text, media_ids=images,
                    in_reply_to_status_id=reply_to)
            else:
                tweet_id = self.api.update_status(
                    status=text, media_ids=images)
        except:
            logging.exception('Tweet with media failed')
            print(sys.exc_info()[0])
            return False
        return tweet_id

    def tweet_text(self, text):
        if TESTING:
            print(text)
            return True
        try:
            tweet_id = self.api.update_status(status=text)
        except:
            logging.exception('Tweet text failed')
            print(sys.exc_info()[0])
            return False
        return tweet_id

    def tweet(self, text, article_id, url, image_path):
        images = list()
        image = self.media_upload(image_path)
        logging.info(f'Media ready with ids: {image}')
        images.append(image)
        logging.info(f'Text to tweet: {text}')
        logging.info(f'Article id: {article_id}')
        reply_to = self.data_provider.get_previous_tweet_id(article_id)
        if reply_to is None:
            logging.info(f'Tweeting url: {url}')
            tweet = self.tweet_text(url)
            # if TESTING, give a random id based on time
            reply_to = tweet.id if not TESTING else time.time()
        logging.info(f'Replying to: {reply_to}')
        tweet = self.tweet_with_media(text, images, reply_to)
        if TESTING:
            # if TESTING, give a random id based on time
            tweet_id = time.time()
        else:
            tweet_id = tweet.id
        logging.info(f'Id to store: {tweet_id}')
        self.data_provider.update_tweet_db(article_id, tweet_id)

    def get_page(self, url, header=None, payload=None):
        r = None
        for x in range(MAX_RETRIES):
            try:
                r = requests.get(url=url, headers=header, params=payload)
            except BaseException as e:
                if x == MAX_RETRIES - 1:
                    print('Max retries reached')
                    logging.warning('Max retries for: %s', url)
                    return None
                if '104' not in str(e):
                    print('Problem with url {}'.format(url))
                    print('Exception: {}'.format(str(e)))
                    logging.exception('Problem getting page')
                    return None
                time.sleep(RETRY_DELAY)
            else:
                break
        return r

    def strip_html(self, html_str):
        """
        a wrapper for bleach.clean() that strips ALL tags from the input
        """
        tags = []
        attr = {}
        styles = []
        strip = True
        return bleach.clean(html_str,
                            tags=tags,
                            attributes=attr,
                            styles=styles,
                            strip=strip)
    
    @staticmethod
    def _is_changed(previous_data, current_data):
        if len(previous_data) == 0 or len(current_data) == 0:
            logging.info('Old or New empty')
            return False
        return previous_data != current_data

    def store_data(self, data):
        if self.data_provider.is_article_tracked(data['article_id']):
            count = self.data_provider.get_article_version_count(data[
                    'article_id'], data['hash'])
            if count != 1:  # Changed
                self.data_provider.add_article_version(data)
                self.tweet_change(data)
        else:
            self.data_provider.track_article(data)


    def tweet_change(self, data):
        previous_version = self.data_provider.get_previous_article_version(data['article_id'])
        url = data['url']
        if self._is_changed(previous_version['title'], data['title']):
            saved_image_diff_path = generate_image_diff(previous_version['title'], data['title'], self.phantomjs_path)
            tweet_text = "שינוי בכותרת"
            self.tweet(tweet_text, data['article_id'], url, saved_image_diff_path)
        if self._is_changed(previous_version['abstract'], data['abstract']):
            saved_image_diff_path = generate_image_diff(previous_version['abstract'], data['abstract'], self.phantomjs_path)
            tweet_text = 'שינוי בתת כותרת'
            self.tweet(tweet_text, data['article_id'], url, saved_image_diff_path)

    def loop_entries(self, entries):
        for article in entries:
            try:
                article_dict = self.entry_to_dict(article)
                current_ids = set()
                if article_dict is not None:
                    self.store_data(article_dict)
                    current_ids.add(article_dict['article_id'])
                self.data_provider.remove_old(current_ids)
            except BaseException as e:
                logging.exception(f'Problem looping entry: {article}')
                print('Exception: {}'.format(str(e)))
                print('***************')
                print(article)
                print('***************')
