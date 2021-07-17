import os
import pandas as pd


class CsvDataProvider:
    def __init__(self, data_files=r"../csvs"):
        self._data_files_dir = data_files
        self.articles = pd.read_csv(os.path.join(data_files, "articles.csv"))
        self.versions = pd.read_csv(os.path.join(data_files, "versions.csv"))

