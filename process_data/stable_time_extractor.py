from time_utils import convert_str_to_timestamp


class StableTimeExtractor(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_cols() -> list:
        return ['stable time']

    @staticmethod
    def extract(data, previous_data, article):
        current_timestamp = data['date_time']
        next_timestamp = data['next date_time']

        return [
            # stable time
            convert_str_to_timestamp(next_timestamp) - convert_str_to_timestamp(current_timestamp)
        ]
