import sys

import datacatalog_tag_manager

if __name__ == '__main__':
    argv = sys.argv
    datacatalog_tag_manager.TagManagerCLI.run(argv[1:] if len(argv) > 0 else argv)
