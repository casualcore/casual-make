import os
import casual.make.platform.common as common
import casual.make.platform.selector as selector
import casual.make.tools.executor as executor
import casual.make.tools.environment as environment
import casual.make.entity.state as state

import sys
import re


######################################################################
##
# compilation and link configuration
##
######################################################################

configuration = selector.build_configuration()

#
# VALGRIND
#
if state.settings.use_valgrind():
    PRE_UNITTEST_DIRECTIVE = "valgrind --xml=yes --xml-file=valgrind.xml".split()

#
# Format the include-/library- paths
#
LIBRARY_PATH_OPTION = "-Wl,-rpath-link="


def library_paths_directive(paths):
    return common.add_item_to_list(paths, '-L') + common.add_item_to_list(paths, LIBRARY_PATH_OPTION)


def library_directive(libraries):

    return common.add_item_to_list(libraries, '-l', common.TargetMethod.LINKNAME)


def local_library_path(paths=[]):
    ld_library_path = environment.get('LD_LIBRARY_PATH','')
    return {'LD_LIBRARY_PATH': 
        ld_library_path + ":" + ":".join(paths)
        }


def escape_space(paths):

    return list(map(lambda string: string.replace(" ", "\\ "), paths))


def normalize_paths(paths):

    return paths


def execute_compile(source, destination, context_directory, paths, directive):

    cmd = configuration.compile.command + configuration.cpp_standard.directive + configuration.compile.directive + \
        configuration.compile.warning.directive + common.casual_build_version() + common.casual_build_commit_hash() + \
        common.optional_flags() + common.optional_possible_flags() + directive + [
        '-o', destination.filename(), source.filename()] + common.add_item_to_list(escape_space(paths), '-I')
    executor.command(cmd, destination, context_directory)


def execute_dependency_generation(source, destination, context_directory, paths, dependency_file):

    cmd = configuration.dependency.command + configuration.dependency.directive + configuration.cpp_standard.directive + [source.filename(
    )] + common.add_item_to_list(escape_space(paths), '-I') + ['-MF', dependency_file]
    executor.command(cmd, destination, context_directory, show_command=False, show_output=False)


def execute_link_library(destination, context_directory, objects, library_paths, libraries):

    cmd = configuration.link.library.command + configuration.link.library.directive + ['-o', destination.filename(
    )] + objects + library_paths_directive(escape_space(library_paths)) + common.add_item_to_list(libraries, '-l', common.TargetMethod.LINKNAME)
    executor.command(cmd, destination, context_directory)


def execute_link_executable(destination, context_directory, objects, library_paths, libraries):

    cmd = configuration.link.executable.command + configuration.link.executable.directive + ['-o', destination.filename(
    )] + objects + library_paths_directive(escape_space(library_paths)) + common.add_item_to_list(libraries, '-l', common.TargetMethod.LINKNAME)
    executor.command(cmd, destination, context_directory)


def execute_link_archive(destination, context_directory, objects):

    cmd = configuration.link.archive.command + configuration.link.archive.directive + [destination.filename()] + objects
    executor.command(cmd, destination, context_directory)


def make_objectname(source):

    return 'obj/' + source.replace('.cpp', '.o').replace('.cc', '.o')


def make_dependencyfilename(name):

    return name.replace('.o', '.d')


def expanded_library_name(name):

    common.verify_type(name)

    assembled = common.assemble_path( name, 'lib', '.so')

    return assembled


def expanded_archive_name(name):

    common.verify_type(name)

    assembled = common.assemble_path( name, 'lib', '.a')

    return assembled


def expanded_executable_name(name):

    common.verify_type(name)

    return name
