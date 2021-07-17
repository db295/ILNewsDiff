import argparse
import itertools

from printer_extractor import PrinterExtractor
from csv_data_provider import CsvDataProvider

FEATURE_EXTRACTORS = [PrinterExtractor]


def process_data(data_files):
    dt = CsvDataProvider(data_files)

    # TODO: setup? - prepare tables/cols
    cols = itertools.chain.from_iterable([extractor.get_cols() for extractor in FEATURE_EXTRACTORS])
    print(list(cols))

    # Extract Features
    for _id, article in dt.articles.iterrows():
        article_versions = dt.versions[(dt.versions["article_id"] == article["article_id"]) &
                                       (dt.versions["article_source"] == article["article_source"])]

        for __id, single_version in article_versions.iterrows():
            past_versions = article_versions[article_versions["version"] < single_version["version"]]
            for feature_extractor in FEATURE_EXTRACTORS:
                feature_extractor.extract(single_version, past_versions, article)


def main():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('datafiles', help='A path to the folders with the csvs')

    args = parser.parse_args()
    process_data(args.datafiles)


if __name__ == "__main__":
    main()
