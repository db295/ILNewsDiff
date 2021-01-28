import collections
import hashlib
from datetime import datetime

from RSSParser import RSSParser

HAARETZ_RSS = "https://www.haaretz.co.il/cmlink/1.1617539"


class HaaretzParser(RSSParser):
    def __init__(self, api, tz, phantomjs_path):
        RSSParser.__init__(self, api, HAARETZ_RSS, phantomjs_path)
        self.tz = tz

    def entry_to_dict(self, article):
        article_dict = dict()
        article_dict['article_id'] = article.guid
        article_dict['url'] = article.link
        article_dict['title'] = article.title
        od = collections.OrderedDict(sorted(article_dict.items()))
        article_dict['hash'] = hashlib.sha224(
            repr(od.items()).encode('utf-8')).hexdigest()
        article_dict['date_time'] = datetime.now(self.tz)
        return article_dict
