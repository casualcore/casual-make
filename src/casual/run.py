#!/usr/bin/env python3


from casual.make.entity import cli, state
from casual.make.platform import selector
import importlib.metadata

def get_installed_version() -> str:
    try:
        return importlib.metadata.version("casual-make-core")
    except importlib.metadata.PackageNotFoundError:
        return "alpha version"

def main():

    args = cli.handle_arguments()

    # handle simples action first
    if args.version:
        print( f"casual-make: {get_installed_version()}")
        raise SystemExit(0)

    state.environment(args)

    selected = args.target

    try:

        # Need to import this after argparse
        from casual.make.entity import model
        from casual.make.tools import handler, output

        # Build the actual model from a file
        output.print("building model: ", end="")
        model.build(args.makefile)

        selected_target = model.get(selected)

        if not selected_target:
            raise SystemError(selected + " not known")

        # construct the dependency tree
        model.construct_dependency_tree(selected_target)

        # retreive the current action list
        actions = model.construct_action_list(selected_target)

        output.print("done")

        if actions:
            output.print(
                f"Using build profile found in {selector.build_profile_file()}"
            )

        if args.list_targets:
            model.list_targets()
            raise SystemExit(1)

        total_handled = 0
        number_of_actions = 0
        if args.statistics:
            for level in actions:
                number_of_actions = number_of_actions + len(level)
            statistics = "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
            output.print("progress: " + statistics)

        # start handling actions
        with handler.Handler() as handler:
            for level in actions:
                # All actions within a 'level' can be done in parallel
                number_of_actions_in_level = len(level)
                handler.handle(level)
                if args.statistics:
                    total_handled = total_handled + number_of_actions_in_level
                    statistics = (
                        "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
                    )
                    output.print("progress: " + statistics)

    except SystemError as exception:
        print(exception)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
