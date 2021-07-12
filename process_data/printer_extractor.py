from feature_extractor import FeatureExtractor


class PrinterExtractor(FeatureExtractor):
    @staticmethod
    def extract(data, previous_data, article):
        print(data)
