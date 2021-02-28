import platform

import casual.make.platform.common as common
import casual.make.tools.environment as environment


CXX = common.cxx()
COMPILER = CXX


def warning_directive():

    return ["-Wall",
            "-Wextra",
            "-Werror",
            "-Wsign-compare",
            "-Wuninitialized",
            "-Winit-self",
            "-Wno-unused-parameter",
            "-Wno-missing-declarations",
            "-Wno-noexcept-type",
            "-Wno-implicit-fallthrough"
            ]


OPTIONAL_FLAGS = common.optional_flags()

VERSION_DIRECTIVE = common.casual_build_version()

# Linkers
LIBRARY_LINKER = CXX
EXECUTABLE_LINKER = common.executable_linker()
ARCHIVE_LINKER = common.archive_linker()

STD_DIRECTIVE = common.cpp_standard()

# lint stuff
LINT_COMMAND = common.lint_command()
LINT_PRE_DIRECTIVES = common.lint_pre_directives()

OPTIONAL_POSSIBLE_FLAGS = common.optional_possible_flags()

# how can we get emmidate binding like -Wl,-z,now ?
GENERAL_LINK_DIRECTIVE = ["-fPIC"]


def compile_directives(warning_directive):
    configuration = VERSION_DIRECTIVE + warning_directive + \
        STD_DIRECTIVE + OPTIONAL_FLAGS + OPTIONAL_POSSIBLE_FLAGS

    if environment.get("CASUAL_MAKE_DEBUG"):
        configuration += ["-ggdb", "-c", "-fPIC"] if platform.system() == 'Darwin' else [
            "-ggdb", "-c", "-fPIC"]

        if environment.get("CASUAL_MAKE_ANALYZE"):
            configuration += ["-fprofile-arcs", "-ftest-coverage"]
    else:
        configuration += ["-c", "-O3", "-fPIC", "-pthread"]

    return configuration


def link_directives_lib(warning_directive):

    configuration = GENERAL_LINK_DIRECTIVE + warning_directive + STD_DIRECTIVE
    if environment.get("CASUAL_MAKE_DEBUG"):
        configuration += ["-ggdb", "-dynamiclib"] if platform.system(
        ) == 'Darwin' else ["-g", "-pthread", "-shared", "-fpic"]

        if environment.get("CASUAL_MAKE_ANALYZE"):
            configuration += ["-fprofile-arcs"] if platform.system() == 'Darwin' else [
                "-O0", "-coverage"]
    else:
        configuration += ["-dynamiclib", "-O3"] if platform.system() == 'Darwin' else [
            "-pthread", "-shared", "-O3", "-fpic"]

    return configuration


def link_directives_exe(warning_directive):

    configuration = GENERAL_LINK_DIRECTIVE + warning_directive + STD_DIRECTIVE
    if environment.get("CASUAL_MAKE_DEBUG"):
        configuration += ["-ggdb"] if platform.system() == 'Darwin' else ["-g",
                                                                          "-pthread", "-fpic"]

        if environment.get("CASUAL_MAKE_ANALYZE"):
            configuration += ["-lgcov", "-fprofile-arcs"] if platform.system() == 'Darwin' else [
                "-O0", "-coverage"]
    else:
        configuration += ["-O3"] if platform.system() == 'Darwin' else [
            "-pthread", "-O3", "-fpic"]

    return configuration


def link_directives_archive(warning_directive):

    configuration = GENERAL_LINK_DIRECTIVE + warning_directive + STD_DIRECTIVE
    if environment.get("CASUAL_MAKE_DEBUG"):
        configuration = ["-ggdb"] if platform.system() == 'Darwin' else ["-g"]
    else:
        configuration = [
            "-O3", "-pthread"] if platform.system() == 'Darwin' else []

    return configuration


def build_configuration(warning_directive=warning_directive()):

    configuration = {
        "compiler": COMPILER,
        "header_dependency_command": COMPILER + ["-E", "-MMD"] + STD_DIRECTIVE,
        "library_linker": LIBRARY_LINKER,
        "executable_linker": EXECUTABLE_LINKER,
        "archive_linker": ARCHIVE_LINKER,
    }

    configuration["compile_directives"] = compile_directives(warning_directive)
    configuration["link_directives_lib"] = link_directives_lib(
        warning_directive)
    configuration["link_directives_exe"] = link_directives_exe(
        warning_directive)
    configuration["link_directives_archive"] = link_directives_archive(
        warning_directive)

    return configuration
