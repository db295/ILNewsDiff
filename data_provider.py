import logging
from typing import Set
import dataset

class DataProvider():

    def __init__(self):
        self.db = dataset.connect('sqlite:///titles.db')
        self.articles_table = self.db['rss_ids']
        self.versions_table = self.db['rss_versions']

    def is_article_tracked(self, article_id: str, article_source: str):
        return self.articles_table.find_one(article_id=article_id, article_source=article_source) is not None

    def track_article(self, data: dict):
        article = {
            'article_id': data['article_id'],
            'article_source': data['article_source'],
            'add_dt': data['date_time'],
            'status': 'home',
            'tweet_id': None
        }
        self.articles_table.insert(article)
        data['version'] = 1
        self.versions_table.insert(data)
        logging.info(f"New article tracked: {data['url']}")
    
    def get_article_version_count(self, artice_id: str, article_source: str, hash: str):
        return self.versions_table.count(
                self.versions_table.table.columns.article_id == artice_id,
                article_source=article_source,
                hash=hash)

    def get_previous_article_version(self, article_id: str, article_source: str):
        return self.db.query(f'SELECT * \
                                FROM rss_versions\
                                WHERE article_id = "{article_id}" \
                                    and article_source = "{article_source} \
                                ORDER BY version DESC \
                                LIMIT 1').next()

    def add_article_version(self, data: dict):
        previous_data_version = self.get_previous_article_version(data['article_id'], data['article_spurce'])
        data['version'] = previous_data_version['version'] + 1
        self.versions_table.insert(data)

    def update_tweet_db(self, article_id: str, article_source: str, tweet_id: str):
        article = {
            'article_id': article_id,
            'article_source': article_source,
            'tweet_id': tweet_id
        }
        self.articles_table.update(article, ['article_id', 'article_source', 'tweet_id'])
        logging.debug('Updated tweet ID in db')
    
    def get_previous_tweet_id(self, article_id: str, article_source: str):
        search = self.articles_table.find_one(article_id=article_id, article_source=article_source)
        if search is None or 'tweet_id' not in search:
            return None
        return search['tweet_id']

    def remove_old(self, current_ids: Set):
        db_ids = set()
        for nota_db in self.articles_table.find(status='home'):
            db_ids.add(nota_db['article_id'])
        for to_remove in (db_ids - current_ids):
            data = dict(article_id=to_remove, status='removed')
            self.articles_table.update(data, ['article_id'])
            logging.info(f'Removed {to_remove}')
