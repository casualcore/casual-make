import argparse
import platform
import subprocess
import json
import casual.make.tools.environment as env

class Settings(object):

    def __init__(self):
        self.model = {}
        self.setup()
        self.deserialize()


    def setup(self):
        self.model["dry_run"] = False
        self.model["raw_format"] = False
        self.model["compiler_handler"] = None
        self.model["extra_args"] = []
        self.model["serial"] = False
        self.model["force"] = False
        self.model["no_colors"] = False
        self.model["quiet"] = False
        self.model["debug"] = False
        self.model["analyze"] = False
        self.model["use_valgrind"] = False
        self.model["ignore_errors"] = False
        self.model["verbose"] = False
        self.model["source_root"] = None


    # convenience functions
    def dry_run(self): return self.model["dry_run"]
    def raw_format(self): return self.model["raw_format"]
    def compiler_handler(self): return self.model["compiler_handler"]
    def extra_args(self): return self.model["extra_args"]
    def serial(self): return self.model["serial"]
    def force(self): return self.model["force"]
    def no_colors(self): return self.model["no_colors"]
    def quiet(self): return self.model["quiet"]
    def debug(self): return self.model["debug"]
    def analyze(self): return self.model["analyze"]
    def use_valgrind(self): return self.model["use_valgrind"]
    def ignore_errors(self): return self.model["ignore_errors"]
    def verbose(self): return self.model["verbose"]
    def source_root(self): return self.model["source_root"]

    # serialize and deserialize to and from environment variable
    def serialize(self):
        serialized = json.dumps( self.model)
        env.set("CASUAL_MAKE_SETTING_SERIALIZED", serialized)

    def deserialize(self):
        deserialized = env.get("CASUAL_MAKE_SETTING_SERIALIZED")
        if deserialized:
            self.model = json.loads(deserialized)


settings = Settings()


def environment(args):
    """
    update environment to manage application flow
    """
    if args.dry_run:
        settings.model["dry_run"] = True
    if args.raw_format:
        settings.model["raw_format"] = True
    # use your own compiler handler with this option
    if args.compiler_handler:
        settings.model["compiler_handler"] = args.compiler_handler
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
            message = "Platform " + platform.system() + " not supported"
            raise SystemError(message)
        settings.model["compiler_handler"] = module
    elif args.compiler == 'cl':
        settings.model["compiler_handler"] = "casual.make.platform.windows"
    else:
        raise SystemError("Compilerhandler not given or not supported")

    if args.extra_args:
        settings.model["extra_args"] = " ".join(args.extra_args)
    if args.serial:
        settings.model["serial"] = True
    if args.force:
        settings.model["force"] = True
    if args.no_colors:
        settings.model["no_colors"] = True
    if args.quiet:
        settings.model["quiet"] = True
    if args.debug:
        settings.model["debug"] = True
    if args.analyze:
        settings.model["analyze"] = True
    if args.use_valgrind:
        settings.model["use_valgrind"] = True
    if args.ignore_errors:
        settings.model["ignore_errors"] = True
    if args.verbose:
        settings.model["verbose"] = True

    if not env.get("CASUAL_MAKE_SOURCE_ROOT"):
        # setup environment
        import importlib
        compiler_handler_module = importlib.import_module(
            settings.compiler_handler())
        gitpath = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"]).rstrip().decode()
        normalized_path = compiler_handler_module.normalize_paths(gitpath)
        settings.model["source_root"] = normalized_path
        env.set("CASUAL_MAKE_SOURCE_ROOT", settings.source_root())
    else:
        settings.model["source_root"] = env.get("CASUAL_MAKE_SOURCE_ROOT")

    # serialize to setting to environment variable to be able to use spawn
    settings.serialize()