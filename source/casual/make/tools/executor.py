from contextlib import contextmanager
import os
import subprocess
import errno
import re
import sys
import casual.make.tools.environment as environment
import casual.make.tools.output as output



# globals
quiet = True if environment.get('CASUAL_MAKE_QUIET') else False
verbose = True if environment.get("CASUAL_MAKE_VERBOSE") else False  

def importCode(file, filename, name, add_to_sys_modules=0):
    """ code can be any object containing code -- string, file object, or
       compiled code object. Returns a new module object initialized
       by dynamically importing the given code and optionally adds it
       to sys.modules under the given name.
    """
    import imp
    module = imp.new_module(name)

    if add_to_sys_modules:
        import sys
        sys.modules[name] = module
    
    code = compile(file.read(), filename, 'exec')
    exec( code, module.__dict__)

    return module


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def create_directory( directory):
   """ 
   We need this construction to avoid race conditions using multiple processes
   That is instead of checking first.
   """
   try:
      os.makedirs(directory)
   except OSError as e:
      if e.errno != errno.EEXIST:
         raise

def execute_raw(command):

   return subprocess.check_output(command).rstrip()

def execute( command, show_command = True, show_output = True, env = None):

   try:
      if show_command and not quiet:
         if "CASUAL_MAKE_RAW_FORMAT" in os.environ:
            output.print( ' '.join( str(v) for v in command), format = False)
         else:
            output.print( ' '.join( str(v) for v in command), end = '') 
      
      out = None if show_output else subprocess.DEVNULL

      err = subprocess.PIPE

      if env:
         # append to global env
         env = dict( os.environ, **env)

      
      if "CASUAL_MAKE_DRY_RUN" not in os.environ:
         reply = subprocess.run( command, stdout = out, stderr = err, check = True, bufsize = 1, env = env)
   
   except KeyboardInterrupt:
      # todo: abort living subprocess here
      raise SystemError("\naborted due to ctrl-c\n")

   except subprocess.CalledProcessError as ex:
      if verbose: output.error( 'processed command: ' + ' '.join( str(v) for v in command))
      if ex.stderr: output.error( ex.stderr.decode(), header = True)
      raise SystemError( "aborting due to errors")


def execute_command( cmd, name = None, directory = None, show_command = True, show_output = True, env = None):

   if directory:
      with cd(directory):
         if name:
            create_directory( os.path.dirname( name.filename))
         execute( cmd, show_command, show_output, env=env)
   else:
      execute( cmd, show_command, show_output, env=env)
