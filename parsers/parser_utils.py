import collections
import hashlib
from datetime import datetime

from html_utils import strip_html


def standard_entry_to_dict(article, source, tz, strip_description=False):
    article_dict = dict()
    article_dict['article_id'] = article.guid
    article_dict['article_source'] = source
    article_dict['url'] = article.link
    article_dict['title'] = article.title
    if strip_description:
        article_dict['abstract'] = strip_html(article['description'])
    else:
        article_dict['abstract'] = article['description']
    od = collections.OrderedDict(sorted(article_dict.items()))
    article_dict['hash'] = hashlib.sha224(repr(od.items()).encode('utf-8')).hexdigest()
    article_dict['date_time'] = datetime.now(tz)
    return article_dict
