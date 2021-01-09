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

def casual_build_version():
   
   return ["-DCASUAL_BUILD_VERSION=\"" + environment.get("CASUAL_BUILD_VERSION", "") + "\""]

def optional_flags():

   return environment.get( "OPTIONAL_FLAGS", "").split()

def cxx():

   return ["g++"] if not environment.get( "CXX") \
      else environment.get( "CXX").split()
 
def lint_command():
   
   return ["clang-tidy"] if not environment.get( "LINT_COMMAND") \
      else environment.get( "LINT_COMMAND").split()

def lint_pre_directives():
   
   return ["-quiet", "-config", "''", "--"] if not environment.get( "LINT_PRE_DIRECTIVES") \
      else environment.get( "LINT_PRE_DIRECTIVES").split()

def executable_linker():
   
   return cxx() if not environment.get( "EXECUTABLE_LINKER") \
      else environment.get( "EXECUTABLE_LINKER").split()
