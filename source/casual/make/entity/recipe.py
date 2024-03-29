import pprint

import distutils.file_util

import os
import time
import sys

from casual.make.entity.target import Target
import casual.make.tools.executor as executor
import casual.make.tools.output as output
import casual.make.entity.state as state


import importlib
compiler_handler_module = state.settings.compiler_handler_module()
selector = importlib.import_module(compiler_handler_module)

action_list = {}
callback_list = []


def find(file, paths):
    for p in paths:
        if os.path.exists(p + '/' + file):
            return p + '/' + file
    return None


def retrieve_filenames(objects):
    files = []
    for item in objects:
        if isinstance(item, Target):
            files.append(item.filename())
        else:
            files.append(item)
    return files


def dump():
    pprint.pprint(action_list)


def execute_dependency_generation(input):
    """
    Recipe for creating dependency includes
    """
    source = input['source']
    destination = input['destination']
    context_directory = os.path.dirname(input['destination'].makefile())
    include_paths = input['include_paths']
    dependency_file = os.path.join(context_directory, input['dependencyfile'])
    selector.execute_dependency_generation(
        source, destination, context_directory, include_paths, dependency_file)


def compile(input):
    """
    Recipe for compiling
    """
    source = input['source']
    destination = input['destination']
    include_paths = input['include_paths']
    context_directory = os.path.dirname(input['destination'].makefile())
    directive = input['directive']

    selector.execute_compile(
        source, destination, context_directory, include_paths, directive)


def link(input):
    """
    Recipe for linking objects to libraries
    """

    destination = input['destination']
    objects = retrieve_filenames(input['objects'])
    context_directory = os.path.dirname(input['destination'].makefile())

    # choose correct flavor of linking
    libraries = input['libraries']
    library_paths = input['library_paths']

    selector.execute_link_library(
        destination, context_directory, objects, library_paths, libraries)


def link_library(input):
    """
    Recipe for linking objects to libraries
    """

    destination = input['destination']
    objects = retrieve_filenames(input['objects'])
    context_directory = os.path.dirname(input['destination'].makefile())

    # choose correct flavor of linking
    libraries = input['libraries']
    library_paths = input['library_paths']

    selector.execute_link_library(
        destination, context_directory, objects, library_paths, libraries)


def link_executable(input):
    """
    Recipe for linking objects to executables
    """

    destination = input['destination']
    objects = retrieve_filenames(input['objects'])
    context_directory = os.path.dirname(input['destination'].makefile())

    libraries = input['libraries']
    library_paths = input['library_paths']

    selector.execute_link_executable(
        destination, context_directory, objects, library_paths, libraries)


def link_archive(input):
    """
    Recipe for linking objects to archives
    """

    destination = input['destination']
    objects = retrieve_filenames(input['objects'])
    context_directory = os.path.dirname(input['destination'].makefile())

    selector.execute_link_archive(destination, context_directory, objects)


def link_unittest(input):
    """
    Recipe for linking objects to executables
    """
    destination = input['destination']
    objects = retrieve_filenames(input['objects'])
    context_directory = os.path.dirname(input['destination'].makefile())

    libraries = input['libraries']
    library_paths = input['library_paths']

    selector.execute_link_executable(
        destination, context_directory, objects, library_paths, libraries)


def test(input):
    testfile = input['destination']
    context_directory = os.path.dirname(input['destination'].makefile())

    library_paths = input['library_paths']
    cmd = [testfile.filename(), "--gtest_color=yes"]
    extra_arguments = state.settings.extra_args()
    if extra_arguments:
        cmd += extra_arguments.split()

    env = selector.local_library_path(library_paths)
    executor.command(cmd, directory=context_directory, env=env)


def install(input):
    source = input['source']
    if isinstance(source, str):
        pass
    elif isinstance(source, Target):
        source = source.filename()
    else:
        source = " ".join(source)

    path = input['path']
    if path[-1] != '/':
        path += '/'
    if not state.settings.dry_run():
        try:
            (filename, copied) = distutils.file_util.copy_file(
                source, path, update=1, verbose=0)
        except:
            os.makedirs(path)
            (filename, copied) = distutils.file_util.copy_file(
                source, path, update=1, verbose=0)

        if copied:
            sys.stdout.write(output.reformat(
                'copy ' + source + ' ' + filename))
    else:
        sys.stdout.write(output.reformat('copy ' + source + ' ' + path))


def clean(input):
    file = input['filename']
    context_directory = os.path.dirname(input['makefile'])

    with executor.cd(context_directory):
        if isinstance(file, Target):
            filename = file.filename()
            if os.path.exists(filename):
                sys.stdout.write(output.reformat("rm -f " + filename))
                if not state.settings.dry_run():
                    os.remove(filename)
        elif isinstance(file, str):
            if os.path.exists(file):
                sys.stdout.write(output.reformat("rm -f " + file))
                if not state.settings.dry_run():
                    os.remove(file)
        else:
            for f in file:
                if isinstance(f, str):
                    filename = f
                else:
                    filename = f.filename()
                if os.path.exists(filename):
                    sys.stdout.write(output.reformat("rm -f " + filename))
                    if not state.settings.dry_run():
                        os.remove(filename)


def dispatch(target):
    """
    This is the core dispatch function
    """
    if target.recipe():
        for recipe in target.recipe():
            recipe.function(recipe.arguments())
