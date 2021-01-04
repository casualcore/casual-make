import os
import casual.make.platform.common as common
import casual.make.tools.executor as executor
import casual.make.tools.environment as environment

import sys
import re


######################################################################
## 
## compilation and link configuration
##
######################################################################

CXX = common.cxx()

COMPILER = CXX

# clang has false warning for noexcept if there are any throws within, even if we catch all
#   we add -Wno-exceptions 
#   TODO: remove as soon as they fix it
WARNING_DIRECTIVE = [
   "-Wall", 
   "-Wextra", 
   "-Wsign-compare", 
   "-Wuninitialized",  
   "-Winit-self", 
   "-Woverloaded-virtual",
   "-Wno-missing-declarations", 
   "-Wno-unused-parameter", 
   "-Wno-implicit-fallthrough"
] 

OPTIONAL_FLAGS = common.optional_flags()

# Linkers
LIBRARY_LINKER = CXX
EXECUTABLE_LINKER = common.executable_linker()
ARCHIVE_LINKER = ["ar", "rcs"]

STD_DIRECTIVE = ["-std=c++17"]

# lint stuff
LINT_COMMAND = common.lint_command()
LINT_PRE_DIRECTIVES = common.lint_pre_directives()

OPTIONAL_POSSIBLE_FLAGS = ["-fcolor-diagnostics"]

# Compile and link directives
#

# how can we get emmidate binding like -Wl,-z,now ?
GENERAL_LINK_DIRECTIVE = ["-fPIC"]

if environment.get( "CASUAL_MAKE_DEBUG"):
   COMPILE_DIRECTIVES = ["-ggdb", "-c", "-fPIC"] + WARNING_DIRECTIVE + STD_DIRECTIVE + OPTIONAL_FLAGS
   LINK_DIRECTIVES_LIB =  ["-ggdb", "-dynamiclib"] + WARNING_DIRECTIVE + GENERAL_LINK_DIRECTIVE
   LINK_DIRECTIVES_EXE =  ["-ggdb"] + WARNING_DIRECTIVE + GENERAL_LINK_DIRECTIVE
   LINK_DIRECTIVES_ARCHIVE =  ["-ggdb"] + WARNING_DIRECTIVE + GENERAL_LINK_DIRECTIVE
   
   if environment.get( "CASUAL_MAKE_ANALYZE"):
      COMPILE_DIRECTIVES += ["-fprofile-arcs", "-ftest-coverage"]
      LINK_DIRECTIVES_LIB += ["-fprofile-arcs"]
      LINK_DIRECTIVES_EXE += ["-lgcov", "-fprofile-arcs"]
else:
   COMPILE_DIRECTIVES =  ["-c", "-O3", "-fPIC"] + WARNING_DIRECTIVE + STD_DIRECTIVE + ["-pthread"] + OPTIONAL_FLAGS
   LINK_DIRECTIVES_LIB = ["-dynamiclib", "-O3"] + GENERAL_LINK_DIRECTIVE + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_EXE = ["-O3"] + GENERAL_LINK_DIRECTIVE + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_ARCHIVE = ["-O3"] + GENERAL_LINK_DIRECTIVE + WARNING_DIRECTIVE + STD_DIRECTIVE + ["-pthread"]


#
# VALGRIND
#
if not environment.get( "CASUAL_MAKE_VALGRIND"):
   PRE_UNITTEST_DIRECTIVE=["valgrind", "--xml=yes", "--xml-file=valgrind.xml"]


#
# Header dependency stuff
#
HEADER_DEPENDENCY_COMMAND = COMPILER + ["-E", "-MMD"] + STD_DIRECTIVE


#
# Directive for setting SONAME
#
LINKER_SONAME_DIRECTIVE = ["-Wl,-dylib_install_name,"]

def library_paths_directive( paths):
   
   return common.add_item_to_list( paths, '-L')

def library_directive(libraries):

   return common.add_item_to_list( libraries, '-l')

def local_library_path(paths = []):

   return {'LD_LIBRARY_PATH' : re.sub( "\s", ":", environment.get('CASUAL_OPTIONAL_LIBRARY_PATHS',''))}

def escape_space( paths):
   
   return map( lambda string: string.replace(" ", "\\ "), paths)

def normalize_paths( paths):

   return paths

def create_compile( source, destination, context_directory, paths, directive):

   cmd = COMPILER + COMPILE_DIRECTIVES + directive + ['-o', destination.filename, source.filename] + common.add_item_to_list( escape_space( paths), '-I')
   executor.execute_command( cmd, destination, context_directory)

def create_includes(source, destination, context_directory, paths, dependency_file):
   
   cmd = HEADER_DEPENDENCY_COMMAND + [source.filename] + common.add_item_to_list( escape_space( paths), '-I') + ['-MF',dependency_file]
   executor.execute_command( cmd, destination, context_directory, show_command=True, show_output=False)

def create_link_library(destination, context_directory, objects, library_paths, libraries):
   
   cmd = LIBRARY_LINKER + LINK_DIRECTIVES_LIB + ['-o', destination.filename] + objects + library_paths_directive( escape_space(library_paths))  + common.add_item_to_list( libraries, '-l')
   executor.execute_command( cmd, destination, context_directory)

def create_link_executable(destination, context_directory, objects, library_paths, libraries):
   
   cmd = EXECUTABLE_LINKER + LINK_DIRECTIVES_EXE + ['-o', destination.filename] + objects + library_paths_directive( escape_space(library_paths)) + common.add_item_to_list( libraries, '-l')
   executor.execute_command( cmd, destination, context_directory)

def create_link_archive(destination, context_directory, objects):

   cmd = ARCHIVE_LINKER + [destination.filename] + objects
   executor.execute_command( cmd, destination, context_directory)

def make_objectname( source):

   return 'obj/' + source.replace( '.cpp', '.o').replace('.cc', '.o')

def make_dependencyfilename( name):

   return name.replace( '.o', '.d')

def expanded_library_name( name, directory = None):
   
   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/' + 'lib' + file + '.so'
   else:
      assembled = directory_part + '/' + 'lib' + file + '.so'

   return os.path.abspath( assembled)

def expanded_archive_name( name, directory = None):
   
   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/' + 'lib' + file + '.a'
   else:
      assembled = directory_part + '/' + 'lib' + file + '.a'

   return os.path.abspath( assembled)

def expanded_executable_name( name, directory = None):

   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/' + file
   else:
      assembled = directory_part + '/' + file

   return os.path.abspath( assembled)
