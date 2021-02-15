import casual.make.tools.environment as environment

import casual.make.compiler.gcc as gcc

import os
import json
import sys



def build_configuration():

   # todo: select correct config

   compiler = environment.get("CXX") or ["g++"]
   type_of_build = "normal" 
   if environment.get( "CASUAL_MAKE_DEBUG"):
      type_of_build = "debug"
   elif environment.get( "CASUAL_MAKE_ANALYZE"):
      type_of_build = "analyze"

   build_configuration_path = environment.get("CASUAL_MAKE_CONFIGURATION_PATH")

   if build_configuration_path:
      if os.path.exists( build_configuration_path):
         with open(build_configuration_path, "r") as file:
            stored_configuration = json.load(file)

         compiler0 = compiler[0]
         if compiler0 in stored_configuration and \
            type_of_build in stored_configuration[compiler0]:
            return stored_configuration[compiler0][type_of_build]
         else:
            print( "configuration not containing all data, using default configuration", file = sys.stderr)

   # use default
   if environment.get("CXX") == 'g++':
      return gcc.build_configuration()

   return gcc.build_configuration()
