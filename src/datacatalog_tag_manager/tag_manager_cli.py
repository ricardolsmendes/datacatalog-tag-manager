import argparse
import logging
import sys

from . import tag_datasource_processor


class TagManagerCLI:

    @classmethod
    def run(cls, argv):
        cls.__setup_logging()

        args = cls._parse_args(argv)
        args.func(args)

    @classmethod
    def __setup_logging(cls):
        logging.basicConfig(level=logging.INFO)

    @classmethod
    def _parse_args(cls, argv):
        parser = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

        subparsers = parser.add_subparsers()

        create_tags_parser = subparsers.add_parser('create', help='Create Tags')
        create_tags_parser.add_argument('--csv-file',
                                        help='CSV file with Tags information',
                                        required=True)
        create_tags_parser.set_defaults(func=cls.__create_tags)

        delete_tags_parser = subparsers.add_parser('delete', help='Delete Tags')
        delete_tags_parser.add_argument('--csv-file',
                                        help='CSV file with Tags information',
                                        required=True)
        delete_tags_parser.set_defaults(func=cls.__delete_tags)

        return parser.parse_args(argv)

    @classmethod
    def __create_tags(cls, args):
        tag_datasource_processor.TagDatasourceProcessor().create_tags_from_csv(
            file_path=args.csv_file)

    @classmethod
    def __delete_tags(cls, args):
        tag_datasource_processor.TagDatasourceProcessor().delete_tags_from_csv(
            file_path=args.csv_file)


def main():
    argv = sys.argv
    TagManagerCLI.run(argv[1:] if len(argv) > 0 else argv)
