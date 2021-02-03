import validators.html_validator
import validators.content_validator
from parsers import parser_utils
from rss_parser import RSSParser

WALLA_RSS = "https://rss.walla.co.il/feed/1?type=main"


class WallaParser(RSSParser):
    def __init__(self, tz):
        RSSParser.__init__(self, WALLA_RSS)
        self.tz = tz

    @staticmethod
    def get_source():
        return "Walla"

    def should_use_first_item_dedup(self):
        return True

    def get_integrity_validators(self):
        return [validators.html_validator]

    def get_tweet_validators(self):
        return [validators.content_validator]

    def entry_to_dict(self, article):
        return parser_utils.standard_entry_to_dict(article, self.get_source(), self.tz, strip_description=True)
