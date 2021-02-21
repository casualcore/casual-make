import os
import sys
import casual.make.platform.common as common
import casual.make.target as target
import casual.make.tools.executor as executor

import re
import cStringIO

include_matcher = re.compile("^Note: including file:\s*(.*)")

######################################################################
## 
## compilation and link configuration
##
######################################################################

COMPILER = ['CL']


WARNING_DIRECTIVE = ["-W3"]

OPTIONAL_FLAGS = common.optional_flags()

VERSION_DIRECTIVE = common.casual_build_version()


# Linkers
LIBRARY_LINKER = ["LINK"]
ARCHIVE_LINKER = ["LINK"]

STD_DIRECTIVE = ["-std:c++14"]

# lint stuff
if not environment.get( "LINT_COMMAND"):
   LINT_COMMAND = ["clang-tidy"]
else:
   LINT_COMMAND = environment.get( "LINT_COMMAND").split()


if not environment.get( "LINT_PRE_DIRECTIVES"):
   LINT_PRE_DIRECTIVES = ["-quiet", "-config", "''", "--"]
else:
   LINT_PRE_DIRECTIVES = environment.get( "LINT_PRE_DIRECTIVES").split()


if not environment.get( "EXECUTABLE_LINKER"):
   EXECUTABLE_LINKER = ["LINK"]
else:
   EXECUTABLE_LINKER = environment.get( "EXECUTABLE_LINKER").split()

# Compile and link directives
#

#
# Compile and link directives
#
if environment.get( "CASUAL_MAKE_DEBUG"):
   COMPILE_DIRECTIVES = ["-Zi", "-c", "-EHsc"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = ["-Zi", "-DLL"]
   LINK_DIRECTIVES_EXE = ["-Zi"]
   LINK_DIRECTIVES_ARCHIVE = ["-Zi"]  

   if environment.get( "CASUAL_MAKE_ANALYZE"):
      COMPILE_DIRECTIVES  += ["-O0", "-coverage"]
      LINK_DIRECTIVES_LIB += ["-O0", "-coverage"]
      LINK_DIRECTIVES_EXE += ["-O0", "-coverage"]
else:
   COMPILE_DIRECTIVES = [ "-c", "-O2", "-EHsc"] + WARNING_DIRECTIVE + STD_DIRECTIVE
   LINK_DIRECTIVES_LIB = [ "-DLL"] 
   LINK_DIRECTIVES_EXE = []
   LINK_DIRECTIVES_ARCHIVE = []


#
# VALGRIND
#
if environment.get( "CASUAL_MAKE_VALGRIND"):
   PRE_UNITTEST_DIRECTIVE="valgrind --xml=yes --xml-file=valgrind.xml".split()


#
# Header dependency stuff
#
HEADER_DEPENDENCY_COMMAND = COMPILER + ["-showIncludes"] + STD_DIRECTIVE + ["-Zs", "-c"]

NOLOGO=['-nologo']

#
# Directive for setting SONAME
#
LINKER_SONAME_DIRECTIVE = ["-Wl,-soname,"]

def append_suffix_in_list( items, suffix):
   new_list = []
   if not items:
      return new_list
      
   for i in items:
      if isinstance( i, target.Target):
         new_list.append( i.name + suffix)
      else:
         new_list.append( i + suffix)
   return new_list

def normalize_paths( paths):
   return paths

def create_dependency_file( data, filename, source, destination, directory):

   output = cStringIO.StringIO()
   output.write(destination + ': \\\n')
   output.write(source + '  \\\n')
   for line in data.split('\n'):
      if 'fatal error' in line:
         raise SystemError(line)
      elif 'Note:' in line and 'Microsoft Visual Studio' not in line and 'Windows Kits' not in line: # no system headers
         result = include_matcher.match(line)
         if result:
            output.write( result.group(1) + ' \\\n')
   dependency_data = output.getvalue()
   output.close()

   with executor.cd(directory):
      if os.path.exists(filename):
         with file(filename, "r") as f:
            content = f.read()
            if content == dependency_data:
			   return

      executor.create_directory( os.path.dirname( filename))
      with file(filename, "w") as f:
         f.write(dependency_data)


def library_paths_directive( paths):

   return common.add_item_to_list( paths, '-LIBPATH:')

def library_directive(libraries):
   
   return append_suffix_in_list( libraries, '.dll')

def execute_compile( source, destination, context_directory, paths, directive):
   
   cmd = COMPILER + COMPILE_DIRECTIVES + directive + ['-Fo:' + destination.filename, source.filename] + common.add_item_to_list( paths, '-I') + NOLOGO
   executor.command( cmd, destination, context_directory)

def execute_dependency_generation(source, destination, context_directory, paths, dependency_file):
   
   cmd = HEADER_DEPENDENCY_COMMAND + [source.filename] + common.add_item_to_list( paths, '-I') + NOLOGO
   dependency_data = executor.command( cmd, destination, context_directory, show_command=True, show_output=True)
   create_dependency_file(dependency_data, dependency_file, source.filename, destination.filename, context_directory)

def execute_link_library(destination, context_directory, objects, library_paths, libraries):

   cmd = ["LIB"] + ['-out:' + destination.filename] + objects + library_paths_directive( library_paths)  + append_suffix_in_list( libraries, '.lib') + NOLOGO
   executor.command( cmd, destination, context_directory)
   cmd = LIBRARY_LINKER + LINK_DIRECTIVES_LIB + ['-out:' + destination.filename.replace(".lib",".dll")] + objects + library_paths_directive( library_paths)  + append_suffix_in_list( libraries, '.lib') + NOLOGO
   executor.command( cmd, destination, context_directory)

def execute_link_executable(destination, context_directory, objects, library_paths, libraries):
   
   cmd = EXECUTABLE_LINKER + LINK_DIRECTIVES_EXE + ['-out:' + destination.filename] + objects + library_paths_directive( library_paths) + append_suffix_in_list( libraries, '.lib') + NOLOGO
   executor.command( cmd, destination, context_directory)

def execute_link_archive(destination, context_directory, objects):

   cmd = ARCHIVE_LINKER + LINK_DIRECTIVES_LIB + ['-out:' + destination.filename] + objects + NOLOGO
   executor.command( cmd, destination, context_directory)

def make_objectname( source):
   
   return 'obj/' + source.replace( '.cpp', '.obj').replace('.cc', '.obj')

def make_dependencyfilename( name):

   return name.replace( '.obj', '.d').replace( '.o', '.d')

def expanded_library_name( name, directory = None):
   
   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/' + file + '.lib'
   else:
      assembled = directory_part + '/' + file + '.lib'

   return os.path.abspath( assembled)

def expanded_archive_name( name, directory = None):
   
   if not isinstance( name, str):
      raise SystemError("Can't call this method with " + str( type( name)))

   directory_part, file = os.path.split( name)

   if directory:
      assembled = directory + '/' + directory_part + '/' + file + '.lib'
   else:
      assembled = directory_part + '/' + file + '.lib'

   return os.path.abspath( assembled)

def expanded_executable_name( name, directory = None):

   return os.path.abspath( name + ".exe")



