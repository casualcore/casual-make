import casual.make.tools.environment as environment
import casual.make.entity.state as state
import casual.make.entity.configuration as configuration

from dataclasses import asdict


import os
import json
import sys
import platform

def build_configuration():

    # todo: select correct config

    compiler = environment.get("CXX") or ["g++"]
    profile = "normal"
    if state.settings.debug():
        profile = "debug"
    elif state.settings.analyze():
        profile = "analyze"

    casual_make_source_root = environment.get("CASUAL_MAKE_SOURCE_ROOT")
    casual_make_home = environment.get("CASUAL_MAKE_HOME")

    if environment.get("CASUAL_MAKE_CONFIGURATION_PATH"):
        build_configuration_path = environment.get("CASUAL_MAKE_CONFIGURATION_PATH")
    elif casual_make_source_root and os.path.exists( os.path.join( casual_make_source_root, ".casual-make", "configuration.json")):
        build_configuration_path = os.path.join( casual_make_source_root, ".casual-make", "configuration.json")
    elif casual_make_home and os.path.exists( os.path.join( casual_make_home, "..", ".casual-make", "configuration.json")):
        build_configuration_path = os.path.join( casual_make_home, "..", ".casual-make", "configuration.json")

    if build_configuration_path:
        if os.path.exists(build_configuration_path):
            with open(build_configuration_path, "r") as file:
                stored_configuration = json.load(file)

            build_configuration = configuration.Configuration( stored_configuration)
            system = platform.system()

            profile_found = build_configuration.profile_find( system, compiler, profile)

            if profile_found:
                return profile_found
            else:
                print(
                    "configuration not containing all data, using default configuration", file=sys.stderr)
    else:
        raise SystemError("No viable compiler configuration found!")
