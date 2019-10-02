import argparse
import logging


class TagManagerCLI:

    @classmethod
    def run(cls):
        cls.__setup_logging()
        args = cls.__parse_args()

    @classmethod
    def __setup_logging(cls):
        logging.basicConfig(level=logging.INFO)

    @classmethod
    def __parse_args(cls):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        return parser.parse_args()
