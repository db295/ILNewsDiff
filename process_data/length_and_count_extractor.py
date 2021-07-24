class LengthAndCountExtractor(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_cols() -> list:
        return ['words_count', 'chars_count', 'special_chars_count', 'size_change',
                'words_addition_count', 'words_removal_count', 'change_ratio']

    @staticmethod
    def count_words(title) -> int:
        return len(title.split(' '))

    @staticmethod
    def count_special_chars(title) -> int:
        special_chars = ['?', '!', '#', '"', '*']
        return sum(title.count(special_char) for special_char in special_chars)

    @staticmethod
    def count_words_addition(title) -> int:
        current_words = title.split(' ')
        previous_words = title.split(' ')

        return len(set(current_words) - set(previous_words))

    @staticmethod
    def count_words_removal(title) -> int:
        current_words = title.split(' ')
        previous_words = title.split(' ')

        return len(set(previous_words) - set(current_words))

    @staticmethod
    def extract(data, previous_data, article):
        title = data['title']
        prev_title = data['prev title']
        return [
            # words_count
            LengthAndCountExtractor.count_words(title),
            # chars_count
            len(title),
            # special_chars_count
            LengthAndCountExtractor.count_special_chars(title),
            # size_change
            abs(len(title) - len(prev_title)),
            # words_addition_count
            LengthAndCountExtractor.count_words_addition(title, prev_title),
            # words_removal_count
            LengthAndCountExtractor.count_words_removal(title, prev_title),
            # change_ratio
            float(abs(len(title) - len(prev_title))) / len(prev_title)
        ]
