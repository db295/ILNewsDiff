import hashlib
import logging
import os
import sys
import time

import bleach
import dataset
from PIL import Image
import requests
from simplediff import html_diff
from selenium import webdriver

if 'TESTING' in os.environ:
    if os.environ['TESTING'] == 'False':
        TESTING = False
    else:
        TESTING = True
else:
    TESTING = True

MAX_RETRIES = 10
RETRY_DELAY = 3


class BaseParser(object):
    def __init__(self, api, phantomjs_path):
        self.articles_table = None
        self.urls = list()
        self.payload = None
        self.articles = dict()
        self.current_ids = set()
        self.filename = str()
        self.db = dataset.connect('sqlite:///titles.db')
        self.api = api
        self.phantomjs_path = phantomjs_path

    def parse(self):
        raise NotImplemented

    def test_twitter(self):
        print(self.api.rate_limit_status())
        print(self.api.me().name)

    def remove_old(self, column='id'):
        db_ids = set()
        for nota_db in self.articles_table.find(status='home'):
            db_ids.add(nota_db[column])
        for to_remove in (db_ids - self.current_ids):
            if column == 'id':
                data = dict(id=to_remove, status='removed')
            else:
                data = dict(article_id=to_remove, status='removed')
            self.articles_table.update(data, [column])
            logging.info('Removed %s', to_remove)

    def get_prev_tweet(self, article_id, column):
        if column == 'id':
            search = self.articles_table.find_one(id=article_id)
        else:
            search = self.articles_table.find_one(article_id=article_id)
        if search is None:
            return None
        else:
            if 'tweet_id' in search:
                return search['tweet_id']
            else:
                return None

    def update_tweet_db(self, article_id, tweet_id, column):
        if column == 'id':
            article = {
                'id': article_id,
                'tweet_id': tweet_id
            }
        else:
            article = {
                'article_id': article_id,
                'tweet_id': tweet_id
            }
        self.articles_table.update(article, [column])
        logging.debug('Updated tweet ID in db')

    def media_upload(self, filename):
        if TESTING:
            return 1
        try:
            response = self.api.media_upload(filename)
        except:
            print(sys.exc_info()[0])
            logging.exception('Media upload')
            return False
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

    def tweet(self, text, article_id, url, column='id'):
        images = list()
        image = self.media_upload('./output/' + self.filename + '.png')
        logging.info('Media ready with ids: %s', image)
        images.append(image)
        logging.info('Text to tweet: %s', text)
        logging.info('Article id: %s', article_id)
        reply_to = self.get_prev_tweet(article_id, column)
        if reply_to is None:
            logging.info('Tweeting url: %s', url)
            tweet = self.tweet_text(url)
            # if TESTING, give a random id based on time
            reply_to = tweet.id if not TESTING else time.time()
        logging.info('Replying to: %s', reply_to)
        tweet = self.tweet_with_media(text, images, reply_to)
        if TESTING:
            # if TESTING, give a random id based on time
            tweet_id = time.time()
        else:
            tweet_id = tweet.id
        logging.info('Id to store: %s', tweet_id)
        self.update_tweet_db(article_id, tweet_id, column)

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

    def show_diff(self, old, new):
        if len(old) == 0 or len(new) == 0:
            logging.info('Old or New empty')
            return False
        new_hash = hashlib.sha224(new.encode('utf8')).hexdigest()
        logging.info(html_diff(old, new))
        html = """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="./css/styles.css">
          </head>
          <body>
          <p>
          {}
          </p>
          </body>
        </html>
        """.format(html_diff(old, new))
        with open('tmp.html', 'w', encoding="utf-8") as f:
            f.write(html)

        driver = webdriver.PhantomJS(
            executable_path=self.phantomjs_path + 'phantomjs')
        driver.get('tmp.html')
        e = driver.find_element_by_xpath('//p')
        start_height = e.location['y']
        block_height = e.size['height']
        end_height = start_height
        start_width = e.location['x']
        block_width = e.size['width']
        end_width = start_width
        total_height = start_height + block_height + end_height
        total_width = start_width + block_width + end_width
        timestamp = str(int(time.time()))
        driver.save_screenshot('./tmp.png')
        img = Image.open('./tmp.png')
        img2 = img.crop((0, 0, total_width, total_height))
        if int(total_width) > int(total_height * 2):
            background = Image.new('RGBA', (total_width, int(total_width / 2)),
                                   (255, 255, 255, 0))
            bg_w, bg_h = background.size
            offset = (int((bg_w - total_width) / 2),
                      int((bg_h - total_height) / 2))
        else:
            background = Image.new('RGBA', (total_width, total_height),
                                   (255, 255, 255, 0))
            bg_w, bg_h = background.size
            offset = (int((bg_w - total_width) / 2),
                      int((bg_h - total_height) / 2))
        background.paste(img2, offset)
        self.filename = timestamp + new_hash
        background.save('./output/' + self.filename + '.png')
        return True

    def __str__(self):
        return '\n'.join(self.urls)
