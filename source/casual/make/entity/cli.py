import argparse

def handle_arguments(arguments = None):
    """
    parsing application arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("target", help="target to handle",
                        nargs='?', default="link")

    parser.add_argument(
        "-d", "--debug", help="compiling with debug flags", action="store_true")
    parser.add_argument(
        "--use-valgrind", help="use valgrind when compiling", action="store_true")
    parser.add_argument("-a", "--analyze",
                        help="build for analyzing", action="store_true")
    parser.add_argument(
        "--dry-run", help="only show the tasks to be done", action="store_true")
    parser.add_argument("-r", "--raw-format",
                        help="echo command in raw format", action="store_true")
    parser.add_argument("-c", "--compiler",
                        help="choose compiler", default="g++")
    parser.add_argument("--compiler-handler",
                        help="choose compiler module directly", default=None)
    parser.add_argument("-s", "--serial", help="compile in a serial maner",
                        action="store_true", default=False)
    parser.add_argument("-f", "--force", help="force action to execute",
                        action="store_true", default=False)
    parser.add_argument("--statistics", help="printout some statistics",
                        action="store_true", default=False)
    parser.add_argument("--no-colors", help="no colors in printouts",
                        action="store_true", default=False)
    parser.add_argument("-i", "--ignore-errors",
                        help="ignore compiler errors", action="store_true")
    parser.add_argument(
        "--quiet", help="do not printout command logging", action="store_true")
    parser.add_argument("-v", "--verbose",
                        help="print some verbose output", action="store_true")
    parser.add_argument(
        "--version", help="print version number", action="store_true")

    parser.add_argument(
        "extra_args", help="argument passed to action", nargs=argparse.REMAINDER)
    args = parser.parse_args(arguments)

    return args


