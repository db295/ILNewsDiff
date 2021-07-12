import argparse

from printer_extractor import PrinterExtractor
from data_provider import DataProvider

FEATURE_EXTRACTORS = [PrinterExtractor]


def process_data(databse_file):
    dt = DataProvider(databse_file)

    # TODO: setup? - prepare tables/cols
    cols = [extractor.get_cols() for extractor in FEATURE_EXTRACTORS]
    print(cols)

    # Extract Features
    for article in dt.articles_table:
        versions = dt.get_ordered_versions(article["article_id"])
        for counter, single_version in enumerate(versions):
            for feature_extractor in FEATURE_EXTRACTORS:
                feature_extractor.extract(single_version, versions[:counter], article)


def main():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('database', help='A path to a database')

    args = parser.parse_args()
    process_data(args.database)


if __name__ == "__main__":
    main()
