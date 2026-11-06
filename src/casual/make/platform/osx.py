import os

from casual.make.platform import common
from casual.make.platform.common import configuration
from casual.make.tools import environment, executor

######################################################################
##
# compilation and link configuration
##
######################################################################


def library_paths_directive(paths):

    return common.add_item_to_list(paths, "-L")


def library_directive(libraries):

    return common.add_item_to_list(libraries, "-l")


def local_library_path(paths=None):
    if paths is None:
        paths = []
    ld_library_path = environment.get("LD_LIBRARY_PATH", "")
    return {"LD_LIBRARY_PATH": ld_library_path + ":" + ":".join(paths)}


def escape_space(paths):

    return (string.replace(" ", "\\ ") for string in paths)


def normalize_paths(paths):

    return paths


def execute_compile(source, destination, context_directory, paths, directive):

    cmd = (
        configuration.instance()["compiler"]
        + configuration.instance()["common_compile_flags"]
        + configuration.instance()["compile_extra"]
        + directive
        + ["-o", destination.filename(), source.filename()]
        + common.add_item_to_list(escape_space(paths), "-I")
    )
    executor.command(cmd, destination, context_directory)


def execute_dependency_generation(
    source, destination, context_directory, paths, dependency_file
):

    cmd = (
        configuration.instance()["header_dependency_command"]
        + [source.filename()]
        + common.add_item_to_list(escape_space(paths), "-I")
        + ["-MF", dependency_file]
    )
    executor.command(
        cmd, destination, context_directory, show_command=False, show_output=False
    )


def execute_link_library(
    destination, context_directory, objects, library_paths, libraries
):

    cmd = (
        configuration.instance()["library_linker"]
        + configuration.instance()["common_link_flags"]
        + configuration.instance()["link_extra_lib"]
        + ["-o", destination.filename()]
        + objects
        + library_paths_directive(escape_space(library_paths))
        + common.add_item_to_list(libraries, "-l")
    )
    executor.command(cmd, destination, context_directory)


def execute_link_executable(
    destination, context_directory, objects, library_paths, libraries
):

    cmd = (
        configuration.instance()["executable_linker"]
        + configuration.instance()["common_link_flags"]
        + configuration.instance()["link_extra_exe"]
        + ["-o", destination.filename()]
        + objects
        + library_paths_directive(escape_space(library_paths))
        + common.add_item_to_list(libraries, "-l")
    )
    executor.command(cmd, destination, context_directory)


def execute_link_archive(destination, context_directory, objects):

    cmd = (
        configuration.instance()["archive_linker"] + [destination.filename()] + objects
    )
    executor.command(cmd, destination, context_directory)


def make_objectname(source):

    return "obj/" + source.replace(".cpp", ".o").replace(".cc", ".o")


def make_dependencyfilename(name):

    return name.replace(".o", ".d")


def expanded_library_name(name, directory=None):

    common.verify_type(name)

    directory_part, file = os.path.split(name)

    assembled = common.assemble_path(directory_part, file, directory, "lib", ".so")

    return os.path.abspath(assembled)


def expanded_archive_name(name, directory=None):

    common.verify_type(name)

    directory_part, file = os.path.split(name)

    assembled = common.assemble_path(directory_part, file, directory, "lib", ".a")

    return os.path.abspath(assembled)


def expanded_executable_name(name, directory=None):

    common.verify_type(name)

    directory_part, file = os.path.split(name)

    assembled = common.assemble_path(directory_part, file, directory)

    return os.path.abspath(assembled)
