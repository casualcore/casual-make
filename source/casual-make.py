#!/usr/bin/env python3

import sys
import subprocess
import os
import platform
import argparse

import casual.make.entity.state as state


def handle_arguments():
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
    args = parser.parse_args()

    return args


def main():

    args = handle_arguments()

    # handle simples action first
    if args.version:
        import casual
        print(casual.__version__)
        raise SystemExit(0)

    state.environment(args)

    selected = args.target

    try:

        # Need to import this after argparse
        import casual.make.entity.model as model
        import casual.make.tools.handler as handler
        import casual.make.tools.executor as executor
        import casual.make.tools.output as output

        # Build the actual model from a file
        output.print("building model: ", end="")
        model.build()

        selected_target = model.get(selected)

        if not selected_target:
            raise SystemError(selected + " not known")

        # construct the dependency tree
        model.construct_dependency_tree(selected_target)

        # retreive the current action list
        actions = model.construct_action_list(selected_target)

        output.print("done")

        total_handled = 0
        number_of_actions = 0
        if args.statistics:
            for level in actions:
                number_of_actions = number_of_actions + len(level)
            statistics = "(" + str(total_handled) + "/" + \
                str(number_of_actions) + ")"
            output.print("progress: " + statistics)

        # start handling actions
        with handler.Handler() as handler:
            for level in actions:
                # All actions within a 'level' can be done in parallel
                number_of_actions_in_level = len(level)
                handler.handle(level)
                if args.statistics:
                    total_handled = total_handled + number_of_actions_in_level
                    statistics = "(" + str(total_handled) + \
                        "/" + str(number_of_actions) + ")"
                    output.print("progress: " + statistics)

    except SystemError as exception:
        print(exception)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
