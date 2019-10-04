import argparse
import logging

from .tag_datasource_processor import TagDatasourceProcessor


class TagManagerCLI:

    @classmethod
    def run(cls):
        cls.__setup_logging()
        cls.__parse_args()

    @classmethod
    def __setup_logging(cls):
        logging.basicConfig(level=logging.INFO)

    @classmethod
    def __parse_args(cls):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        subparsers = parser.add_subparsers()

        create_tags_parser = subparsers.add_parser('create-tags', help='Create Tags')
        create_tags_parser.add_argument('--csv-file', help='CSV file with Tags information', required=True)
        create_tags_parser.set_defaults(func=cls.__create_tags)

        args = parser.parse_args()
        args.func(args)

    @classmethod
    def __create_tags(cls, args):
        TagDatasourceProcessor().create_tags_from_csv(file_path=args.csv_file)
