#!/usr/bin/env python3

import sys
import subprocess
import os
import platform

import casual.make.entity.state as state
import casual.make.entity.cli as cli

def main():

    args = cli.handle_arguments()

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
