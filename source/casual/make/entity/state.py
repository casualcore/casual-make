import argparse
import platform
import subprocess

import casual.make.tools.environment as env


class Settings(object):
    def __init__(self):
        self.dry_run = False
        self.raw_format = False
        self.compiler_handler = None
        self.extra_args = []
        self.serial = False
        self.force = False
        self.no_colors = False
        self.quiet = False
        self.debug = False
        self.analyze = False
        self.use_valgrind = False
        self.ignore_errors = False
        self.verbose = False
        self.source_root = None


settings = Settings()


def environment(args):
    """
    update environment to manage application flow
    """
    if args.dry_run:
        settings.dry_run = True
    if args.raw_format:
        settings.raw_format = True
    # use your own compiler handler with this option
    if args.compiler_handler:
        settings.compiler_handler = args.compiler_handler
    # use built-in compiler handler which uses g++
    elif args.compiler == 'g++':
        module = None
        if platform.system() == 'Darwin':
            module = "casual.make.platform.osx"
        elif platform.system() == 'Linux':
            module = "casual.make.platform.linux"
        elif platform.system().startswith('CYGWIN'):
            module = "casual.make.platform.cygwin"
        else:
            SystemError("Platform not supported")
        settings.compiler_handler = module
    elif args.compiler == 'cl':
        settings.compiler_handler = "casual.make.platform.windows"
    else:
        raise SystemError("Compilerhandler not given or not supported")

    if args.extra_args:
        settings.extra_args = " ".join(args.extra_args)
    if args.serial:
        settings.serial = True
    if args.force:
        settings.force = True
    if args.no_colors:
        settings.no_colors = True
    if args.quiet:
        settings.quiet = True
    if args.debug:
        settings.debug = True
    if args.analyze:
        settings.analyze = True
    if args.use_valgrind:
        settings.use_valgrind = True
    if args.ignore_errors:
        settings.ignore_errors = True
    if args.verbose:
        settings.verbose = True

    if not env.get("CASUAL_MAKE_SOURCE_ROOT"):
        # setup environment
        import importlib
        compiler_handler_module = importlib.import_module(
            settings.compiler_handler)
        gitpath = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"]).rstrip().decode()
        normalized_path = compiler_handler_module.normalize_paths(gitpath)
        settings.source_root = normalized_path
        env.set("CASUAL_MAKE_SOURCE_ROOT", settings.source_root)
