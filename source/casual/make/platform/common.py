import platform
import casual.make.entity.state as state

import casual.make.entity.target as target
import casual.make.tools.environment as environment

import os
import subprocess

from enum import Enum

class FileType(Enum):
    SOURCE = 1
    DESTINATION = 2

class TargetMethod(Enum):
    NAME = 1
    FILENAME = 2
    LINKNAME = 3

def create_absolute_filename( filename, directory, file_type=FileType.SOURCE):
    if not os.path.isabs(filename):
        if file_type == FileType.SOURCE:
            return os.path.normpath( os.path.abspath(directory + '/' + filename))
        else:
            rel_path = os.path.relpath( directory, state.settings.source_root())
            return os.path.normpath( os.path.join( environment.get("CASUAL_MAKE_BUILD_ROOT"), rel_path, filename))
    else:
        return os.path.normpath(filename)
    
def use_build_directory( directory):
    return os.path.normpath( os.path.join( environment.get("CASUAL_MAKE_BUILD_ROOT"), os.path.relpath( directory, state.settings.source_root())))

def add_item_to_list(items, item, target_method=TargetMethod.NAME):
    new_list = []
    if not items:
        return new_list

    for i in items:
        if isinstance(i, target.Target):
            if target_method == TargetMethod.FILENAME and i.filename():
                new_list.append(item + i.filename())
            elif target_method == TargetMethod.LINKNAME and i.linkname():
                new_list.append(item + i.linkname())
            else:
                new_list.append(item + i.name())
        else:
            new_list.append(item + i)
    return new_list


def verify_type(name):
    if not isinstance(name, str):
        raise SystemError("Can't call this method with " + str(type(name)))


def assemble_path(filename, prefix="", suffix=""):

    directory, file = os.path.split(filename)

    assembled = os.path.join(directory, prefix + file + suffix)

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
