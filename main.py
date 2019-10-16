import sys

from datacatalog_tag_manager import TagManagerCLI

if __name__ == '__main__':
    argv = sys.argv
    TagManagerCLI.run(argv[1:] if len(argv) > 0 else argv)
