import platform

import casual.make.entity.target as target
import casual.make.tools.environment as environment

import os
import subprocess


def add_item_to_list(items, item):
    new_list = []
    if not items:
        return new_list

    for i in items:
        if isinstance(i, target.Target):
            new_list.append(item + i.name())
        else:
            new_list.append(item + i)
    return new_list


def verify_type(name):
    if not isinstance(name, str):
        raise SystemError("Can't call this method with " + str(type(name)))


def assemble_path(sub_directory, name, main_directory=None, prefix="", suffix=""):

    if main_directory:
        assembled = os.path.join(
            main_directory, sub_directory, prefix + name + suffix)
    else:
        assembled = os.path.join(sub_directory, prefix + name + suffix)

    return assembled


def casual_build_version():
    if environment.get("CASUAL_MAKE_BUILD_VERSION"):
        return ["-DCASUAL_MAKE_BUILD_VERSION=\"" + environment.get("CASUAL_MAKE_BUILD_VERSION") + "\""]
    else:
        return []


def casual_build_commit_hash():
    try:
        githash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]).rstrip().decode()
        return ["-DCASUAL_MAKE_COMMIT_HASH=\"" + githash + "\""]
    except:
        return []


def optional_flags():

    return environment.get("OPTIONAL_FLAGS", "").split()


def cxx():

    return ["g++"] if not environment.get("CXX") \
        else environment.get("CXX").split()


def lint_command():

    return ["clang-tidy"] if not environment.get("LINT_COMMAND") \
        else environment.get("LINT_COMMAND").split()


def lint_pre_directives():

    return ["-quiet", "-config", "''", "--"] if not environment.get("LINT_PRE_DIRECTIVES") \
        else environment.get("LINT_PRE_DIRECTIVES").split()


def executable_linker():

    return cxx() if not environment.get("EXECUTABLE_LINKER") \
        else environment.get("EXECUTABLE_LINKER").split()


def archive_linker():
    return ["ar", "rcs"]


def cpp_standard():
    if platform.system().startswith('CYGWIN'):
        return ["-std=gnu++23"]
    else:
        return ["-std=c++2b"]


def optional_possible_flags():
    return ["-fdiagnostics-color=always"]
