import argparse
import itertools

import pandas as pd

from printer_extractor import PrinterExtractor
from word_token_extractor import WordsTokensExtractor
from csv_data_provider import CsvDataProvider

COLUMNS_TO_KEEP = ["id", "version", "article_id", "article_source", "title", "amount_of_words"]

ROW_EXTRACTED = {
    # "amount_of_words": WordsTokensExtractor.how_many_words
}

FEATURE_EXTRACTORS = [
    # WordsTokensExtractor,
    # PrinterExtractor
]


def process_data(data_files, clean_csv, out_version, in_version=0):
    # TODO: choose which features to extract
    dt = CsvDataProvider(data_files, in_version)

    if clean_csv:
        # The data we want to keep from the csvs
        extracted_features = dt.versions[COLUMNS_TO_KEEP]
    else:
        extracted_features = dt.versions

    # cols based on the same row data -
    for col_name, f in ROW_EXTRACTED.items():
        extracted_features[col_name] = dt.versions.apply(f, axis=1, result_type="expand")

    if len(FEATURE_EXTRACTORS) > 0:
        # cols based on a lot of data -
        cols = list(itertools.chain.from_iterable([extractor.get_cols() for extractor in FEATURE_EXTRACTORS]))
        processed_data = pd.DataFrame(columns=cols)
        row_id = 0

        # Extract Features
        for _id, article in dt.articles.iterrows():
            article_versions = dt.versions[(dt.versions["article_id"] == article["article_id"]) &
                                           (dt.versions["article_source"] == article["article_source"])]

            for __id, single_version in article_versions.iterrows():
                past_versions = article_versions[article_versions["version"] < single_version["version"]]
                processed_row = []
                for feature_extractor in FEATURE_EXTRACTORS:
                    processed_row.extend(feature_extractor.extract(single_version, past_versions, article))

                processed_data.loc[row_id] = processed_row
                row_id += 1

    # TODO: export back to csv
    print(f"Max words - {extracted_features['amount_of_words'].max()}")
    out_file = dt.versions_file_format.format(version=out_version)
    extracted_features.to_csv(out_file)

    print("Done!!")


def main():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('datafiles', help='A path to the folders with the csvs')
    parser.add_argument('--in-version', default=0, help='Which version to use')
    parser.add_argument('--out-version', help='Which version to write')

    parser.add_argument('--clean', action="store_true", help='Should keep only important data')

    args = parser.parse_args()
    process_data(args.datafiles, args.clean, args.out_version, args.in_version)


if __name__ == "__main__":
    main()
