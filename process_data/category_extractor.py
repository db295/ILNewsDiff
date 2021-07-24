class CategoryExtractor(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_cols() -> list:
        return ['category', 'type']

    @staticmethod
    def extract_article_category(current_version_data) -> str:
        article_source = current_version_data['article_source']
        article_url = current_version_data['url']
        article_id = current_version_data['article_id']

        if 'Haaretz' == article_source:
            # There are many cases, handle them
            # Structure is https://www.haaretz.co.il/family/askingforafriend/BLOG-1.9467825
            # https://www.haaretz.co.il/blogs/sherenf/BLOG-1.9497746
            return ' '.join(article_url.split('/')[3:-1])
        elif 'Walla' == article_source:
            # Structure is https://news.walla.co.il/item/3415909
            return article_url.split('/')[2].split('.')[0]
        elif 'IsraelHayom' == article_source:
            # NEXT_VERSION: Maybe we can use BERT to get category or search for key words
            return 'Unknown'

        raise Exception(f"Unknown article source {article_source} for article {article_id},"
                        f" with id {current_version_data['id']}")

    @staticmethod
    def extract_article_type(current_version_data) -> str:
        article_source = current_version_data['article_source']
        article_url = current_version_data['url']
        article_id = current_version_data['article_id']

        if 'Haaretz' == article_source:
            # Structure is https://www.haaretz.co.il/news/world/.premium-LIVE-1.9481685 and
            # without prefix to id in regular items
            article_identifiers = article_url.split('/')[-1].split('-')[:-1]
            return ' '.join(article_identifiers) if len(article_identifiers) > 0 else 'item'
        elif 'Walla' == article_source:
            # Structure is https://news.walla.co.il/item/3415909
            return article_url.split('/')[-2]
        elif 'IsraelHayom' == article_source:
            # Structure is https://www.israelhayom.co.il/opinion/846019
            return article_url.split('/')[-2]

        raise Exception(f"Unknown article source {article_source} for article {article_id},"
                        f" with id {current_version_data['id']}")

    @staticmethod
    def extract(data, previous_data, article):
        return [
            # category
            CategoryExtractor.extract_article_category(data),
            # type
            CategoryExtractor.extract_article_type(data)
        ]
