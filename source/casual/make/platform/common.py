import casual.make.entity.target as target

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
   if not os.getenv( "OPTIONAL_FLAGS"):
      return []
   else:
      return os.getenv( "OPTIONAL_FLAGS").split()

def cxx():
   if not os.getenv( "CXX"):
      return ["g++"]
   else:
      return os.getenv( "CXX").split()

def lint_command():
   if not os.getenv( "LINT_COMMAND"):
      return ["clang-tidy"]
   else:
      return os.getenv( "LINT_COMMAND").split()

def lint_pre_directives():
   if not os.getenv( "LINT_PRE_DIRECTIVES"):
      return ["-quiet", "-config", "''", "--"]
   else:
      return os.getenv( "LINT_PRE_DIRECTIVES").split()

def executable_linker():
   if not os.getenv( "EXECUTABLE_LINKER"):
      return cxx()
   else:
      return os.getenv( "EXECUTABLE_LINKER").split()
