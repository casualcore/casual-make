import os
import casual.make.platform.common as common
import casual.make.tools.executor as executor
import casual.make.tools.environment as environment

import sys
import re

def compose_paths( *args):
   paths=''
   root_path = environment.get("CASUAL_REPOSITORY_ROOT")
   for arg in args:
      path = os.path.join(root_path,arg)
      paths += executor.execute_raw(['cygpath', path]) + ':'
   reply = paths[:-1]
   return reply


######################################################################
## 
## compilation and link configuration
##
######################################################################


CXX = common.cxx()

COMPILER = CXX

#
# -Wno-noexcept-type  we can probably remove this on g++ 8
# -Wno-implicit-fallthrough remove and add [[fallthrough] attribute, when we're on c++17
#
WARNING_DIRECTIVE = ["-Wall",
 "-Wextra",
 "-Werror",
 "-Wsign-compare",
 "-Wuninitialized",
 "-Winit-self",
# "-Woverloaded-virtual", add when g++ fixes (possible) bug
 "-Wno-unused-parameter",
 "-Wno-deprecated-declarations",
 "-Wno-missing-declarations",
 "-Wno-noexcept-type",
 "-Wno-class-memaccess",
 "-Wno-implicit-fallthrough",
 "-Wa,-mbig-obj"]


OPTIONAL_FLAGS = common.optional_flags()

VERSION_DIRECTIVE = common.casual_build_version()


# Linkers
LIBRARY_LINKER = CXX
EXECUTABLE_LINKER = common.executable_linker()
ARCHIVE_LINKER = ["ar", "rcs"]

STD_DIRECTIVE = ["-std=gnu++17"]

#
# Lint stuff
#
LINT_COMMAND = common.lint_command()
LINT_PRE_DIRECTIVES = common.lint_pre_directives()

OPTIONAL_POSSIBLE_FLAGS = ["-fcolor-diagnostics"]




#
# Compile and link directives
#
if environment.get( "CASUAL_MAKE_DEBUG"):
   COMPILE_DIRECTIVES = ["-g", "-pthread", "-c", "-fpic"] + VERSION_DIRECTIVE + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = ["-g", "-pthread", "-shared", "-fpic"]
   LINK_DIRECTIVES_EXE = ["-g", "-pthread", "-fpic"]
   LINK_DIRECTIVES_ARCHIVE = ["-g"]  

   if environment.get( "CASUAL_MAKE_ANALYZE"):
      COMPILE_DIRECTIVES  += ["-O0", "-coverage"]
      LINK_DIRECTIVES_LIB += ["-O0", "-coverage"]
      LINK_DIRECTIVES_EXE += ["-O0", "-coverage"]
else:
   COMPILE_DIRECTIVES = [ "-pthread", "-c", "-O3", "-fpic"] + VERSION_DIRECTIVE + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = [ "-pthread", "-shared", "-O3", "-fpic"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_EXE = [ "-pthread", "-O3", "-fpic"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_ARCHIVE = []


#
# VALGRIND
#
if not environment.get( "CASUAL_MAKE_VALGRIND"):
   PRE_UNITTEST_DIRECTIVE=["valgrind", "--xml=yes", "--xml-file=valgrind.xml"]


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

TOOLS_LIBRARY_PATHS = compose_paths( 'middleware/common/bin',
   'middleware/configuration/bin')

def library_paths_directive( paths):

   return common.add_item_to_list( paths, '-L') + common.add_item_to_list( paths, LIBRARY_PATH_OPTION)

def library_directive(libraries):
   
   return common.add_item_to_list( libraries, '-l')

def local_library_path( paths = []):
   
   reply = {
      'PATH' : environment.get('PATH','') + ':' + \
      re.sub( "\s", ":", environment.get('CASUAL_OPTIONAL_LIBRARY_PATHS','')) + \
         ':' + TOOLS_LIBRARY_PATHS
      }

   if paths:
      extra_path = compose_paths( *paths)
      reply['PATH'] += ':' + extra_path

   return reply

def escape_space( paths):

   return map( lambda string: string.replace(" ", "\\ "), paths)

def normalize_paths( paths):

   if isinstance( paths, list):
      normalized = []
      for path in paths:
         normalized.append( executor.execute_raw(['cygpath', path]))
      return normalized
   elif isinstance( paths, str):
      return executor.execute_raw(['cygpath', paths])
   else:
      raise SystemError( "Error normlizing path: ", paths) 

def create_compile( source, destination, context_directory, paths, directive):
   
   cmd = COMPILER + COMPILE_DIRECTIVES + directive + ['-o', destination.filename, source.filename] + common.add_item_to_list( escape_space( paths), '-I')
   executor.command( cmd, destination, context_directory)

def create_includes(source, destination, context_directory, paths, dependency_file):
   
   cmd = HEADER_DEPENDENCY_COMMAND + [source.filename] + common.add_item_to_list( escape_space( paths), '-I') + ['-MF',dependency_file] 
   executor.command( cmd, destination, context_directory, show_command=True, show_output=False)

def create_link_library(destination, context_directory, objects, library_paths, libraries):

   #archive_name = destination.filename + '.a' # cygwin-style
   #archive_name = destination.filename.replace('.dll','.a') # mingw-style
   #archive_name = destination.filename + '.lib' # cygwin-style
   #archive_name = destination.filename.replace('.dll','.lib') # mingw-style
   #cmd = LIBRARY_LINKER + LINK_DIRECTIVES_LIB + ['-o', destination.filename] + \
   #   ['-Wl,--out-implib=' + archive_name] + \
   #   ['-Wl,--export-all-symbols'] + \
   #   ['-Wl,--enable-auto-import'] + \
   #   ['-Wl,--whole-archive'] + objects + \
   #   ['-Wl,--no-whole-archive'] + library_paths_directive( library_paths) + common.add_item_to_list( libraries, '-l')
   cmd = LIBRARY_LINKER + LINK_DIRECTIVES_LIB + ['-o', destination.filename] + \
      objects + \
      library_paths_directive( escape_space( library_paths)) + \
      common.add_item_to_list( libraries, '-l')
   executor.command( cmd, destination, context_directory)

def create_link_executable(destination, context_directory, objects, library_paths, libraries):
   
   cmd = EXECUTABLE_LINKER + LINK_DIRECTIVES_EXE + ['-o', destination.filename] + objects + library_paths_directive( escape_space( library_paths)) + common.add_item_to_list( libraries, '-l')
   executor.command( cmd, destination, context_directory)

def create_link_archive(destination, context_directory, objects):

   cmd = ARCHIVE_LINKER + [destination.filename] + objects
   executor.command( cmd, destination, context_directory)

def make_objectname( source):
   
   return 'obj/' + source.replace( '.cpp', '.o').replace('.cc', '.o')

def make_dependencyfilename( name):
   
   return name.replace( '.o', '.d')

def expanded_library_name( name, directory = None):
   
   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/lib' + file + '.dll'
   else:
      assembled = directory_part + '/lib' + file + '.dll'

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

   return os.path.abspath( assembled) + '.exe'
