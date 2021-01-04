import casual.make.entity.target as target
import casual.make.tools.environment as environment

import os

def add_item_to_list( items, item):
   new_list = []
   if not items:
      return new_list
      
   for i in items:
      if isinstance( i, target.Target):
         new_list.append( item + i.name)
      else:
         new_list.append( item + i)
   return new_list

def optional_flags():
   if not environment.get( "OPTIONAL_FLAGS"):
      return []
   else:
      return environment.get( "OPTIONAL_FLAGS").split()

def cxx():
   if not environment.get( "CXX"):
      return ["g++"]
   else:
      return environment.get( "CXX").split()

def lint_command():
   if not environment.get( "LINT_COMMAND"):
      return ["clang-tidy"]
   else:
      return environment.get( "LINT_COMMAND").split()

def lint_pre_directives():
   if not environment.get( "LINT_PRE_DIRECTIVES"):
      return ["-quiet", "-config", "''", "--"]
   else:
      return environment.get( "LINT_PRE_DIRECTIVES").split()

def executable_linker():
   if not environment.get( "EXECUTABLE_LINKER"):
      return cxx()
   else:
      return environment.get( "EXECUTABLE_LINKER").split()
