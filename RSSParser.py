import logging
import feedparser

from BaseParser import BaseParser


class RSSParser(BaseParser):
    def __init__(self, api, rss_url, phantomjs_path):
        BaseParser.__init__(self, api, phantomjs_path)
        self.urls = rss_url
        self.articles_table = self.db['rss_ids']
        self.versions_table = self.db['rss_versions']

    def entry_to_dict(self, article):
        raise NotImplemented()

    def store_data(self, data):
        if self.articles_table.find_one(article_id=data['article_id']) is None:  # New
            self.track_article(data)
        else:
            count = self.versions_table.count(
                self.versions_table.table.columns.article_id == data[
                    'article_id'],
                hash=data['hash'])
            if count == 1:  # Existing
                pass
            else:  # Changed
                self.tweet_change(data)

    def tweet_change(self, data):
        result = self.db.query('SELECT * \
                                       FROM rss_versions\
                                       WHERE article_id = "%s" \
                                       ORDER BY version DESC \
                                       LIMIT 1' % (data['article_id']))
        for row in result:
            data['version'] = row['version'] + 1
            self.versions_table.insert(data)
            url = data['url']
            if row['title'] != data['title']:
                if self.show_diff(row['title'], data['title']):
                    tweet_text = "שינוי בכותרת"
                    self.tweet(tweet_text, data['article_id'], url, 'article_id')
            if row['abstract'] != data['abstract']:
                if self.show_diff(row['abstract'], data['abstract']):
                    tweet_text = 'שינוי בתת כותרת'
                    self.tweet(tweet_text, data['article_id'], url, 'article_id')

    def track_article(self, data):
        article = {
            'article_id': data['article_id'],
            'add_dt': data['date_time'],
            'status': 'home',
            'tweet_id': None
        }
        self.articles_table.insert(article)
        logging.info('New article tracked: %s', data['url'])
        data['version'] = 1
        self.versions_table.insert(data)

    def loop_entries(self, entries):
        if len(entries) == 0:
            return False
        for article in entries:
            try:
                article_dict = self.entry_to_dict(article)
                if article_dict is not None:
                    self.store_data(article_dict)
                    self.current_ids.add(article_dict['article_id'])
            except BaseException as e:
                logging.exception('Problem looping RSS: %s', article)
                print('Exception: {}'.format(str(e)))
                print('***************')
                print(article)
                print('***************')
                return False
        return True

    def parse(self):
        r = feedparser.parse(self.urls[0])
        if r is None:
            logging.warning('Empty response RSS')
            return
        else:
            logging.info('Parsing %s', r.channel.title)
        loop = self.loop_entries(r.entries)
        if loop:
            self.remove_old('article_id')
