class BasicInfoExtractor(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_cols() -> list:
        return ['id', 'article_id', 'version', 'url', 'timestamp', 'source']

    @staticmethod
    def extract_article_id(current_version_data) -> str:
        article_source = current_version_data['article_source']
        article_id = current_version_data['article_id']

        if 'Haaretz' == article_source:
            # Structure is 1.9497004
            return ''.join(str(article_id).split('.'))
        elif 'Walla' == article_source:
            # Structure is https://news.walla.co.il/item/3415909
            return article_id.split('/')[-1]
        elif 'IsraelHayom' == article_source:
            # Structure is '846021 at https://www.israelhayom.co.il'
            return article_id.split(' ')[0]

        raise Exception(f"Unknown article source {article_source} for article {article_id},"
                        f" with id {current_version_data['id']}")

    @staticmethod
    def extract(data, previous_data, article):
        return {
            'id': data['id'],
            'article_id': BasicInfoExtractor.extract_article_id(data),
            'version': data['version'],
            'url': data['url'],
            'timestamp': data['date_time'],
            'source': data['article_source']
        }
