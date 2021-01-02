from contextlib import contextmanager
import os
import subprocess
import errno
import re
import sys
import casual.make.tools.color as color_module


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

def reformat( line):
    """ reformat output from make and add som colours"""
    
    for regex in reformat.ingore_filters:
        match = regex.match( line)
        if match:
            return ''
     
    for regex, filter in reformat.filters:
        match = regex.match( line)
      
        if match:
            return filter( match)
        
    return line


reformat.ingore_filters = [
   re.compile(r'(^make.*)Nothing to be done for'),
]

reformat.filters = [ 
    [ re.compile(r'(^(g|c|clang)\+\+).* -o (\S+\.o) (\S+\.cc|\S+\.cpp|\S+\.c).*'),
     lambda match: color_module.color.green( 'compile: ') + color_module.color.white( match.group(4)) + '\n' ],
    [ re.compile(r'(^(g|c|clang)\+\+).* -E .*?(\S+\.cc|\S+\.cpp|\S+\.c).*'),
     lambda match: color_module.color.green( 'dependency: ') + color_module.color.white( match.group(3)) + '\n' ],
    [ re.compile(r'(^ar) \S+ (\S+\.a).*'),  
     lambda match: color_module.color.blue( 'archive: ') + color_module.color.white( match.group(2)) + '\n' ],
    [ re.compile(r'(^(g|c|clang)\+\+).* -o (\S+).*(?:(\S+\.o) ).*'),
     lambda match: color_module.color.blue( 'link: ') + color_module.color.white( match.group(3)) + '\n' ],
    [ re.compile(r'^(.*[.]cmk )(.*)'),  
     lambda match: color_module.color.cyan( 'makefile: ') + color_module.color.blue( match.group(2) ) + ' ' + match.group(1) + '\n'],
    [ re.compile(r'(^make.*:)(.*)'),  
     lambda match: color_module.color.header( match.group(1) ) + match.group(2) + '\n'],
    [ re.compile(r'^rm -f (.*)'),  
     lambda match: color_module.color.header( 'delete: ' ) + match.group(1) + '\n' ],
    [ re.compile(r'^mkdir( [-].+)*[ ](.*)'),  
     lambda match: color_module.color.header( 'create: ' ) + match.group( 2) + '\n' ],
    [ re.compile(r'.*casual-build-server[\S\s]+-c (\S+)[\s]+-o (\S+) .*'),  
     lambda match: color_module.color.blue( 'buildserver: ' ) + color_module.color.white( match.group(2)) + '\n' ],
    [ re.compile(r'^copy +(\S+) (.*)'),  
     lambda match: color_module.color.blue( 'prepare install: ') + color_module.color.white( match.group(1)) +  ' --> ' +  color_module.color.white(match.group(2)) + '\n' ],
    [ re.compile(r'^(>[a-zA-Z+.]+)[\s]+(.*)'),  
     lambda match: color_module.color.green( 'updated: ') + match.group(2) + ' ' + color_module.color.blue( match.group(1)) + '\n' ],
    [ re.compile(r'^(.*/bin/test-.*)'),  
     lambda match: color_module.color.cyan( 'unittest: ') + color_module.color.white( match.group(1)) + '\n' ],
    [ re.compile(r'^casual-build-resource-proxy.*--output[ ]+([^ ]+)'),  
     lambda match: color_module.color.blue( 'build-rm-proxy: ') + color_module.color.white( match.group(1)) +'\n' ],
    [ re.compile(r'^ln -s (.*?) (.*)'),  
     lambda match: color_module.color.blue( 'symlink: ') + color_module.color.white( match.group(2)) + ' --> ' + color_module.color.white( match.group(1)) + '\n' ],
    [ re.compile(r'^[^ ]*clang-tidy (.*?) (.*)'),  
     lambda match: color_module.color.green( 'lint: ') + color_module.color.white( match.group(1)) + '\n' ],
    
]

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
      if show_command:
         if "CASUAL_RAW_FORMAT" in os.environ:
            sys.stdout.write( ' '.join( str(v) for v in command) + '\n')
         else:
            sys.stdout.write( reformat( ' '.join( str(v) for v in command)))
      
      output = sys.stdout

      if not show_output:
         output = open( os.devnull, 'w')

      if env:
         # append to global env
         env = dict( os.environ, **env)

      
      if "CASUAL_MAKE_DRY_RUN" not in os.environ:
         reply = subprocess.run( command, stdout = output, check = True, bufsize = 1, env = env)

   except KeyboardInterrupt:
      # todo: abort living subprocess here
      raise SystemError("\naborted due to ctrl-c\n")

   except subprocess.CalledProcessError as ex:
      if ex.stderr: sys.stderr.write(ex.stderr)
      raise


def execute_command( cmd, name = None, directory = None, show_command = True, show_output = True, env = None):
   try:
      if directory:
         with cd(directory):
            if name:
               create_directory( os.path.dirname( name.filename))
            execute( cmd, show_command, show_output, env=env)
      else:
         execute( cmd, show_command, show_output, env=env)
   except subprocess.CalledProcessError as e:
      raise SystemError( e.output)