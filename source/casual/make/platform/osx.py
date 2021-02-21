import os
import casual.make.platform.common as common
import casual.make.platform.selector as selector
import casual.make.tools.executor as executor
import casual.make.tools.environment as environment

import sys
import re


######################################################################
## 
## compilation and link configuration
##
######################################################################


build_configuration = selector.build_configuration()

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

def execute_compile( source, destination, context_directory, paths, directive):

   cmd = build_configuration['compiler'] + build_configuration['compile_directives'] + ['-o', destination.filename(), source.filename()] + common.add_item_to_list( escape_space( paths), '-I')
   executor.command( cmd, destination, context_directory)

def execute_dependency_generation(source, destination, context_directory, paths, dependency_file):
   
   cmd = build_configuration['header_dependency_command'] + [source.filename()] + common.add_item_to_list( escape_space( paths), '-I') + ['-MF',dependency_file]
   executor.command( cmd, destination, context_directory, show_command=True, show_output=False)

def execute_link_library(destination, context_directory, objects, library_paths, libraries):
   
   cmd = build_configuration['library_linker'] + build_configuration['link_directives_lib']  + ['-o', destination.filename()] + objects + library_paths_directive( escape_space(library_paths))  + common.add_item_to_list( libraries, '-l')
   executor.command( cmd, destination, context_directory)

def execute_link_executable(destination, context_directory, objects, library_paths, libraries):
   
   cmd = build_configuration['executable_linker'] + build_configuration['link_directives_exe'] + ['-o', destination.filename()] + objects + library_paths_directive( escape_space(library_paths)) + common.add_item_to_list( libraries, '-l')
   executor.command( cmd, destination, context_directory)

def execute_link_archive(destination, context_directory, objects):

   cmd = build_configuration['archive_linker'] + [destination.filename()] + objects
   executor.command( cmd, destination, context_directory)

def make_objectname( source):

   return 'obj/' + source.replace( '.cpp', '.o').replace('.cc', '.o')

def make_dependencyfilename( name):

   return name.replace( '.o', '.d')

def expanded_library_name( name, directory = None):
   
   common.verify_type( name)

   directory_part, file = os.path.split( name)

   assembled = common.assemble_path( directory_part, file, directory, 'lib', '.so')

   return os.path.abspath( assembled)

def expanded_archive_name( name, directory = None):
   
   common.verify_type( name)

   directory_part, file = os.path.split( name)

   assembled = common.assemble_path( directory_part, file, directory, 'lib', '.a')

   return os.path.abspath( assembled)

def expanded_executable_name( name, directory = None):
   
   common.verify_type( name)

   directory_part, file = os.path.split( name)

   assembled = common.assemble_path( directory_part, file, directory)

   return os.path.abspath( assembled)
