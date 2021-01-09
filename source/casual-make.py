#!/usr/bin/env python3

import sys
import subprocess
import os
import platform
import argparse

import casual.make.tools.environment as environment

def handle_arguments():
   """
   parsing application arguments
   """
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
   parser.add_argument( "--quiet", help="do not printout command logging", action="store_true")
   parser.add_argument( "-v", "--verbose", help="print some verbose output", action="store_true")
   parser.add_argument( "--version", help="print version number", action="store_true")

   parser.add_argument( "extra_args", help="argument passed to action", nargs=argparse.REMAINDER)
   args = parser.parse_args()

   return args

def set_environment( args):
   """
   update environment to manage application flow
   """
   if args.dry_run: environment.set("CASUAL_MAKE_DRY_RUN")
   if args.raw_format: environment.set("CASUAL_MAKE_RAW_FORMAT")
   # use your own compiler handler with this option
   if args.compiler_handler: environment.set("CASUAL_MAKE_COMPILER_HANDLER", args.compiler_handler)
   # use built-in compiler handler which uses g++
   elif args.compiler == 'g++':
      module = None
      if platform.system() == 'Darwin': module = "casual.make.platform.osx"
      elif platform.system() == 'Linux': module = "casual.make.platform.linux"
      elif platform.system().startswith('CYGWIN'): module = "casual.make.platform.cygwin"
      else: SystemError("Platform not supported")
      environment.set("CASUAL_MAKE_COMPILER_HANDLER", module)
   elif args.compiler == 'cl': environment.set("CASUAL_MAKE_COMPILER_HANDLER", "casual.make.platform.windows")
   else: raise SystemError("Compilerhandler not given or not supported")

   if args.extra_args: environment.set("CASUAL_MAKE_COMMANDLINE_EXTRA_ARGUMENTS", " ".join(args.extra_args))
   if args.parallel: sys.stdout.write( "Deprecated option --parallel. This is default now. Use --serial instead to do opposite\n")
   if args.serial: environment.set("CASUAL_MAKE_SERIAL_EXECUTION")
   if args.force: environment.set("CASUAL_MAKE_FORCE_EXECUTION")
   if args.no_colors: environment.set("CASUAL_MAKE_NO_COLORS")
   if args.quiet: environment.set("CASUAL_MAKE_QUIET")
   if args.debug: environment.set("CASUAL_MAKE_DEBUG")
   if args.analyze: environment.set("CASUAL_MAKE_ANALYZE")
   if args.use_valgrind: environment.set("CASUAL_MAKE_VALGRIND")
   if args.ignore_errors: environment.set("CASUAL_MAKE_IGNORE_ERROR")
   if args.verbose: environment.set("CASUAL_MAKE_VERBOSE")

def main():

   args = handle_arguments()

   # handle simples action first
   if args.version:
      import casual
      print (casual.__version__)
      raise SystemExit(0)

   set_environment( args)

   selected=args.target

   try:

      # Need to import this after argparse
      import casual.make.entity.model as model
      import casual.make.tools.handler as handler
      import casual.make.tools.executor as executor
      import casual.make.tools.output as output

      # Build the actual model from a file
      output.print( "building model: ", end='')
      model.build()

      selected_target = model.get( selected)
      
      if not selected_target: raise SystemError( selected + " not known")

      # construct the dependency tree
      model.construct_dependency_tree( selected_target)

      # retreive the current action list
      actions = model.construct_action_list( selected_target)

      output.print("done")

      total_handled = 0
      number_of_actions = 0
      if args.statistics:
         for level in actions:
            number_of_actions = number_of_actions + len( level)
         statistics = "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
         output.print("progress: " + statistics)
      
      # start handling actions
      with handler.Handler() as handler:
         for level in actions:
            # All actions within a 'level' can be done in parallel
            number_of_actions_in_level = len(level)
            handler.handle( level)
            if args.statistics:
               total_handled = total_handled + number_of_actions_in_level
               statistics = "(" + str(total_handled) + "/" + str(number_of_actions) + ")"
               output.print("progress: " + statistics)

   except SystemError as exception:
      print( exception)
      raise SystemExit( 1)   

if __name__ == "__main__":
   main()
