#!/usr/bin/env python3

import sys
import subprocess
import os
import time
import platform

import pprint

import argparse

def usage():
   print ( "usage: "+ sys.argv[0] + " target" )
   raise SystemExit


def main():

   parser = argparse.ArgumentParser()

   parser.add_argument( "target", help="target to handle", nargs='?', default="link")
   parser.add_argument( "-d","--debug", help="compiling with debug flags", action="store_true")
   parser.add_argument( "--use-valgrind", help="use valgrind when compiling", action="store_true")
   parser.add_argument( "-a", "--analyze", help="build for analyzing", action="store_true")
   parser.add_argument( "--dry-run", help="only show the tasks to be done", action="store_true")
   parser.add_argument( "-r","--raw-format", help="echo command in raw format", action="store_true")
   parser.add_argument( "-c","--compiler", help="choose compiler", default="g++")
   parser.add_argument( "--compiler-handler", help="choose compiler module directly", default=None)
   parser.add_argument( "-p", "--parallel", help="compile in a parallel maner. This is default now. Will be removed", required=False, action="store_true")
   parser.add_argument( "-s", "--serial", help="compile in a serial maner", action="store_true", default=False)
   parser.add_argument( "-f", "--force", help="force action to execute", action="store_true", default=False)
   parser.add_argument( "--statistics", help="printout some statistics", action="store_true", default=False)
   parser.add_argument( "--no-colors", help="no colors in printouts", action="store_true", default=False)
   parser.add_argument( "-i", "--ignore-errors", help="ignore compiler errors", action="store_true")

   parser.add_argument( "extra_args", help="argument passed to action", nargs=argparse.REMAINDER)
   args = parser.parse_args()

   selected=args.target

   if args.dry_run: os.environ["CASUAL_MAKE_DRY_RUN"] = "1"
   if args.raw_format: os.environ["CASUAL_RAW_FORMAT"] = "1"
   # use your own compiler handler with this option
   if args.compiler_handler: os.environ["CASUAL_COMPILER_HANDLER"] = args.compiler_handler
   # use built-in compiler handler which uses g++
   elif args.compiler == 'g++':
      if platform.system() == 'Darwin': module = "casual.make.platform.osx"
      elif platform.system() == 'Linux': module = "casual.make.platform.linux"
      elif platform.system().startswith('CYGWIN'): module = "casual.make.platform.cygwin"
      else: SystemError("Platform not supported")
      os.environ["CASUAL_COMPILER_HANDLER"] = module
   elif args.compiler == 'cl': os.environ["CASUAL_COMPILER_HANDLER"] = "casual.make.platform.windows"
   else: raise SystemError("Compilerhandler not given or not supported")

   if args.extra_args: os.environ["CASUAL_COMMANDLINE_EXTRA_ARGUMENTS"] = " ".join(args.extra_args)
   if args.parallel: sys.stdout.write( "Deprecated option --parallel. This is default now. Use --serial instead to do opposite\n")
   if args.serial: os.environ["CASUAL_SERIAL_EXECUTION"] = "1"
   if args.force: os.environ["CASUAL_FORCE_EXECUTION"] = "1"
   if args.no_colors: os.environ["CASUAL_NO_COLORS"] = "1"
   try:

      # Need to import this after argparse
      import casual.make.entity.model as model
      import casual.make.tools.handler as handler
      import casual.make.tools.executor as executor

      # handle normalize path
      import importlib
      compiler_handler = os.getenv("CASUAL_COMPILER_HANDLER")
      compiler_handler_module = importlib.import_module( compiler_handler)

      # setup environment
      gitpath = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).rstrip()
      normalized_path = compiler_handler_module.normalize_paths( gitpath).decode()
      os.environ["CASUAL_REPOSITORY_ROOT"] = normalized_path

      # Build the actual model from a file
      print( executor.reformat( "building model: "), end='')

      model.build()

      selected_target = model.get( selected)
      
      if not selected_target:
         raise SystemError( selected + " not known")

      model.construct_dependency_tree( selected_target)

      actions = model.construct_action_list( selected_target)

      print("done")

      total_handled = 0
      number_of_actions = 0
      if args.statistics:
         statistics = None
         for level in actions:
            number_of_actions = number_of_actions + len( level)
            statistics = "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
         print("progress: " + statistics)
      
      with handler.Handler() as handler:
         for level in actions:
            # All actions within a 'level' can be done in parallel
            number_of_actions_in_level = len(level)
            handler.handle( level)
            if args.statistics:
               total_handled = total_handled + number_of_actions_in_level
               statistics = "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
               print("progress: " + statistics)

   except SystemError as exception:
      print( exception)
      raise SystemExit( 1)   

if __name__ == "__main__":
   main()