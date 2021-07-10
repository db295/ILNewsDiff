import argparse


def process_data(databse_file):
    pass


def main():
    parser = argparse.ArgumentParser(description='Process some data.')
    parser.add_argument('database', help='A path to a database')

    args = parser.parse_args()
    process_data(args.database)


if __name__ == "__main__":
    main()
