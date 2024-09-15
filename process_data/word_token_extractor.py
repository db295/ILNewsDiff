from feature_extractor import FeatureExtractor


class WordsTokensExtractor(FeatureExtractor):
    @staticmethod
    def get_cols() -> list:
        return ["amount_of_words", "title"]

    @staticmethod
    def how_many_words(data):
        return data.title.count(" ") + 1

    @staticmethod
    def extract(data, previous_data, article):
        amount_of_words = WordsTokensExtractor.how_many_words(data)
        return [amount_of_words, data.title]
