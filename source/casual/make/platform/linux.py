import os
import casual.make.platform.common as common
import casual.make.tools.executor as executor

import sys
import re



######################################################################
## 
## compilation and link configuration
##
######################################################################


CXX = common.cxx()
COMPILER = CXX


#
# -Wno-noexcept-type  we can probably remove this on g++ 8
# -Wno-implicit-fallthrough remove and add [[fallthrough]] attribute, when we're on c++17
#
WARNING_DIRECTIVE = ["-Wall",
 "-Wextra",
 "-Werror",
 "-Wsign-compare",
 "-Wuninitialized",
 "-Winit-self",
 "-Woverloaded-virtual",
 "-Wno-unused-parameter",
 "-Wno-missing-declarations",
 "-Wno-noexcept-type",
 "-Wno-implicit-fallthrough"]

OPTIONAL_FLAGS = common.optional_flags()

# Linkers
LIBRARY_LINKER = CXX
EXECUTABLE_LINKER = common.executable_linker()
ARCHIVE_LINKER = ["ar", "rcs"]

STD_DIRECTIVE = ["-std=c++17"]

# lint stuff
LINT_COMMAND = common.lint_command()
LINT_PRE_DIRECTIVES = common.lint_pre_directives()

#
# Compile and link directives
#
if os.getenv( "DEBUG"):
   COMPILE_DIRECTIVES = ["-g", "-pthread", "-c", "-fpic",] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = ["-g", "-pthread", "-shared", "-fpic"]
   LINK_DIRECTIVES_EXE = ["-g", "-pthread", "-fpic"]
   LINK_DIRECTIVES_ARCHIVE = ["-g"]  

   if os.getenv( "ANALYZE"):
      COMPILE_DIRECTIVES  += ["-O0", "-coverage"]
      LINK_DIRECTIVES_LIB += ["-O0", "-coverage"]
      LINK_DIRECTIVES_EXE += ["-O0", "-coverage"]
else:
   COMPILE_DIRECTIVES = [ "-pthread", "-c", "-O3", "-fpic"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = [ "-pthread", "-shared", "-O3", "-fpic"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_EXE = [ "-pthread", "-O3", "-fpic"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_ARCHIVE = []


#
# VALGRIND
#
if os.getenv( "VALGRIND"):
   PRE_UNITTEST_DIRECTIVE="valgrind --xml=yes --xml-file=valgrind.xml".split()

#
# Format the include-/library- paths
# 
LIBRARY_PATH_OPTION = "-Wl,-rpath-link="

#
# Header dependency stuff
#
HEADER_DEPENDENCY_COMMAND = COMPILER + ["-E", "-MMD"] + STD_DIRECTIVE

#
# Directive for setting SONAME
#
LINKER_SONAME_DIRECTIVE = ["-Wl,-soname,"]


def library_paths_directive( paths):

   return common.add_item_to_list( paths, '-L') + common.add_item_to_list( paths, LIBRARY_PATH_OPTION)

def library_directive(libraries):
   
   return common.add_item_to_list( libraries, '-l')

def local_library_path(paths = []):

   return {'LD_LIBRARY_PATH' : re.sub( "\s", ":", os.getenv('CASUAL_OPTIONAL_LIBRARY_PATHS',''))}

def normalize_paths( paths):
   
   return paths

def create_compile( source, destination, context_directory, paths, directive):
   
   cmd = COMPILER + COMPILE_DIRECTIVES + directive + ['-o', destination.filename, source.filename] + common.add_item_to_list( paths, '-I')
   executor.execute_command( cmd, destination, context_directory)

def create_includes(source, destination, context_directory, paths, dependency_file):
   
   cmd = HEADER_DEPENDENCY_COMMAND + [source.filename] + common.add_item_to_list( paths, '-I') + ['-MF',dependency_file] 
   executor.execute_command( cmd, destination, context_directory, show_command=True, show_output=False)

def create_link_library(destination, context_directory, objects, library_paths, libraries):

   cmd = LIBRARY_LINKER + LINK_DIRECTIVES_LIB + ['-o', destination.filename] + objects + library_paths_directive( library_paths)  + common.add_item_to_list( libraries, '-l')
   executor.execute_command( cmd, destination, context_directory)

def create_link_executable(destination, context_directory, objects, library_paths, libraries):
   
   cmd = EXECUTABLE_LINKER + LINK_DIRECTIVES_EXE + ['-o', destination.filename] + objects + library_paths_directive( library_paths) + common.add_item_to_list( libraries, '-l')
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
