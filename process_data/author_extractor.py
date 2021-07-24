NOT_NAMES = [
    'askingforafriend',
    'cookingwithkids',
    'touchfood',
    'sohowsitgoing',
    'latinit',
    'homeschooling',
    'photoblog',
    'somethingtoread'
]


class AuthorExtractor(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_cols() -> list:
        return ['author']

    @staticmethod
    def extract_author_from_blog_url(blog_url):
        url_parts = blog_url.split('/')
        optional_author_name = url_parts[-2]
        return optional_author_name if optional_author_name not in NOT_NAMES else "Unknown"

    @staticmethod
    def extract_author(current_version_data) -> str:
        article_source = current_version_data['article_source']
        article_url = current_version_data['url']

        if article_source in ['Walla', 'IsraelHayom']:
            return "Unknown"
        elif 'Haaretz' == article_source:
            key_words = ['BLOG', 'HIGHLIGHT']
            if any([key_word in article_url.split('/')[-1] for key_word in key_words]):
                return AuthorExtractor.extract_author_from_blog_url(article_url)

        raise Exception(f"Unknown article source {article_source} for article {article_id},"
                        f" with id {current_version_data['id']}")

    @staticmethod
    def extract(data, previous_data, article):
        return {
            'author': AuthorExtractor.extract_author(data)
        }
