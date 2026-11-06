import json
import os
import platform
from importlib import resources

from casual.make.entity import state
from casual.make.tools import environment


def file_or_none(file):
    if os.path.exists(file):
        return file

    return None


def build_profile_file():

    candidates = (
        environment.get("CASUAL_MAKE_CONFIGURATION_PATH"),
        os.path.join(state.settings.source_root(), ".casual", "toolchain.json"),
        resources.files("casual.make").joinpath("toolchain.json"),
    )

    build_configuration_path = next(
        (file for path in candidates if path and (file := file_or_none(path))),
        None,  # Standardvärde om ingen fil hittas
    )

    if build_configuration_path:
        return build_configuration_path

    raise SystemError("No valid build profiles found!")


def build_configuration():

    compiler = (environment.get("CXX") or "g++").split()

    type_of_build = "normal"
    if state.settings.debug():
        type_of_build = "debug"
    elif state.settings.analyze():
        type_of_build = "analyze"

    build_configuration_path = build_profile_file()

    with open(build_configuration_path, "r") as file:
        stored_configuration = json.load(file)

    system = platform.system()
    compiler0 = compiler[0]
    if system in stored_configuration and compiler0 in stored_configuration[system]:
        return (
            stored_configuration[system][compiler0]["defaults"]
            | stored_configuration[system][compiler0]["profiles"][type_of_build]
        )
    else:
        raise SystemError("No valid build profiles found!")
