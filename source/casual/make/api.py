import inspect
import os

import casual.make.model as model
import casual.make.recipe as recipe
from casual.make.target import Target, Recipe
from casual.make.tools.executor import importCode

#
# global setup for operations
#
compile_target = model.register( 'compile')
compile_target.need_serial_execution = False

link_target = model.register( 'link')
link_target.need_serial_execution = False

link_library_target = model.register( 'link-library')
link_library_target.need_serial_execution = False

link_archive_target = model.register( 'link-archive')
link_archive_target.need_serial_execution = False

link_executable_target = model.register( 'link-executable')
link_executable_target.need_serial_execution = False

link_unittest_target = model.register( 'link-unittest')
link_unittest_target.need_serial_execution = False


test_target = model.register('test')
# this operations should be done no matter what when referenced
test_target.execute = True
test_target.need_serial_execution = True

clean_target = model.register( 'clean')
# this operations should be done no matter what when referenced
clean_target.execute = True
clean_target.need_serial_execution = True

dependency_target = model.register( 'dependency')
dependency_target.execute = True
dependency_target.need_serial_execution = False

link_target.add_dependency( [link_library_target, link_archive_target, link_executable_target, link_unittest_target])

install_target = model.register('install')
# this operations should be done no matter what when referenced
install_target.execute = True
install_target.need_serial_execution = False

import importlib
compiler_handler = os.getenv("CASUAL_COMPILER_HANDLER")
compiler_handler_module = importlib.import_module( compiler_handler)

#
# Helpers
#
def caller():

   name = inspect.getouterframes( inspect.currentframe())[2][1]
   path = os.path.abspath( name)
   target = model.register(name=path, filename=path, makefile = path) 
   return target

def absolute_path( filename, makefile):
   if os.path.isabs( filename):
      return filename
   directory, dummy = os.path.split( makefile)
   assembled = directory + '/' + filename
   return os.path.abspath( assembled)

def normalize_library_target( libs, paths = None):
   reply = []
   for lib in libs:
      if not isinstance( lib, Target):
         target = model.get( lib, paths)
         if not target:
            lib = model.register( lib)
         else:
            lib = target
      reply.append( lib)
   return reply

# Helpers
def includes( dependency_file, makefile):

   context_directory, dummy = os.path.split(makefile)
   if os.path.exists( dependency_file):
      with open( dependency_file ) as file:
         files = file.read()
      files = files.replace('\\\n','\n')
      reply=[]
      for f in (files.split()[1:]):
         filename = f.rstrip()
         if os.path.isabs( filename):
            abs_path = filename
         else:
            abs_path = os.path.abspath( context_directory + '/' + filename)
         item = model.store.register( abs_path, abs_path, makefile)

         reply.append( item)
      return reply
   else:
      return []

#
# Main DSL
#
def Compile( sourcefile, objectfile = None, directive = []):
   """
   Compile code to object files
   """
   makefile = caller()

   if not objectfile:
      objectfile = compiler_handler_module.make_objectname( sourcefile)

   dependencyfile = compiler_handler_module.make_dependencyfilename( objectfile)
   dependencyfile_target = model.register(name=dependencyfile, filename=absolute_path( dependencyfile, makefile.filename), makefile = makefile.filename) 
   dependencies = includes( dependencyfile_target.filename, makefile = makefile.filename)

   source_target = model.register(name=sourcefile, filename=absolute_path(sourcefile, makefile.filename), makefile = makefile.filename)
   
   if len( dependencies) == 0:
      # no dependency file - add at least source file
      dependencies = [source_target]
   
   # add makefile to dependency
   dependencies.append( makefile)

   object_target = model.register(name=objectfile, filename=absolute_path(objectfile, makefile.filename), makefile = makefile.filename)
   
   arguments = { 
      'destination' : object_target, 
      'dependencyfile' :  dependencyfile,
      'source' : source_target, 
      'include_paths' : model.include_paths( makefile.filename),
      'directive' : directive
      }

   object_target.add_recipe( Recipe( recipe.create_includes, arguments))
   object_target.add_recipe( Recipe( recipe.compile, arguments))

   object_target.add_dependency( dependencies)

   compile_target.add_dependency( object_target)

   clean_target.add_recipe( Recipe( recipe.clean, {'filename' : [ object_target, dependencyfile_target], 'makefile': makefile.filename}))
 
   dependencyfile_target.add_recipe( Recipe( recipe.create_includes, arguments))
   dependencyfile_target.execute = True
   dependency_target.add_dependency( dependencyfile_target)

   return object_target

def Link( destination, objects, libs):
   """
   Link object files to shared objects
   """

   return LinkLibrary( destination, objects, libs)

def LinkLibrary( destination, objects, libs):
   """
   Link object files to shared objects library
   """
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename)
   name = os.path.basename(destination)
   full_library_name = compiler_handler_module.expanded_library_name( destination, directory)
   library_target = model.register(name=name, filename=full_library_name, makefile = makefile.filename)

   library_paths = model.library_paths( makefile.filename)
   normalized_library_targets = normalize_library_target( libs, paths = library_paths)
   arguments = {
      'destination' : library_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   library_target.add_recipe( Recipe( recipe.link_library, arguments))
   library_target.add_dependency( objects + normalized_library_targets)

   link_library_target.add_dependency( [library_target, makefile])

   clean_target.add_recipe( Recipe( recipe.clean, {'filename' : [library_target], 'makefile': makefile.filename}))

   return library_target

def LinkArchive( destination, objects):
   """
   Link object files to archive
   """
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename)
   name=os.path.basename(destination)

   full_archive_name = compiler_handler_module.expanded_archive_name( destination, directory)
   archive_target = model.register(name=name, filename=full_archive_name, makefile = makefile.filename)
   arguments = {
      'destination' : archive_target, 
      'objects' : objects
      }

   archive_target.add_recipe ( Recipe( recipe.link_archive, arguments))
   archive_target.add_dependency( objects)

   link_archive_target.add_dependency( [archive_target, makefile])

   clean_target.add_recipe( Recipe( recipe.clean, {'filename' : [archive_target], 'makefile': makefile.filename}))

   return archive_target

def LinkExecutable( destination, objects, libs):
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename)

   full_executable_name = compiler_handler_module.expanded_executable_name(destination, directory)
   executable_target = model.register( full_executable_name, full_executable_name, makefile = makefile.filename)
   library_paths = model.library_paths( makefile.filename)
   normalized_library_targets = normalize_library_target( libs, library_paths)
   arguments = {
      'destination' : executable_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   executable_target.add_recipe( Recipe( recipe.link_executable, arguments))
   executable_target.add_dependency( objects + normalized_library_targets)

   link_executable_target.add_dependency( [executable_target, makefile])

   clean_target.add_recipe( Recipe( recipe.clean, {'filename' : [executable_target], 'makefile': makefile.filename}))

   return executable_target

def LinkUnittest( destination, objects, libs):
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename)

   full_executable_name = compiler_handler_module.expanded_executable_name(destination, directory)
   executable_target = model.register( full_executable_name, full_executable_name, makefile = makefile.filename)
   library_paths = model.library_paths( makefile.filename)
   normalized_library_targets = normalize_library_target( libs, library_paths) + normalize_library_target([ 'gtest', 'gtest_main' ])
   arguments = {
      'destination' : executable_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   executable_target.add_recipe( Recipe( recipe.link_unittest, arguments))
   executable_target.add_dependency( objects + normalized_library_targets)

   link_unittest_target.add_dependency( [executable_target, makefile])

   clean_target.add_recipe( Recipe( recipe.clean, {'filename' : [executable_target], 'makefile': makefile.filename}))
 
   test_executable_target = model.register( "test-" + destination, destination, makefile = makefile.filename)
   test_executable_target.add_recipe( Recipe( recipe.test,
      {
         'destination' : executable_target,
         'library_paths': library_paths
      }) 
   )
   test_executable_target.execute = True
   test_executable_target.need_serial_execution = True

   test_executable_target.add_dependency( executable_target)
   test_target.add_dependency( test_executable_target)

   return executable_target

def Install( source, path):
   
   makefile = caller()
   if not source:
      return None

   if not isinstance( source, list):
      source = [source]

   for item in source:
      if isinstance( item, tuple):
         install_file_target = model.register( 'install_' + item[0], makefile = makefile.filename)
         dependency_target = model.get( item[0])
         if not dependency_target:
            filename = os.path.abspath( os.path.dirname( makefile.filename) + '/' + item[0])
            dependency_target = model.register( item[0], filename, makefile = makefile.filename)
         install_file_target.add_dependency( dependency_target)
         install_file_target.execute = True
         install_file_target.need_serial_execution = False
         arguments = {
            'source' : dependency_target.filename, 
            'path' : path + '/' + item[1]
         }
         install_file_target.add_recipe( Recipe( recipe.install, arguments))
         install_target.add_dependency( install_file_target)
      elif isinstance( item, model.Target):
         install_file_target = model.register( 'install_' + item.name, makefile = makefile.filename)
         dependency_target = item
         install_file_target.add_dependency( dependency_target)
         install_file_target.execute = True
         arguments = {
            'source' : dependency_target.filename, 
            'path' : path
         }
         install_file_target.add_recipe( Recipe( recipe.install, arguments))
         install_target.add_dependency( install_file_target)
      else:
         install_file_target = model.register('install_' + item, makefile = makefile.filename)
         dependency_target = model.get( item)
         if not dependency_target:
            filename = os.path.abspath( os.path.dirname( makefile.filename) + '/' + item)
            dependency_target = model.register( item, filename, makefile = makefile.filename)
         install_file_target.add_dependency( dependency_target)
         install_file_target.execute = True
         arguments = {
            'source' : dependency_target.filename, 
            'path' : path 
         }
         install_file_target.add_recipe( Recipe( recipe.install, arguments))
         install_target.add_dependency( install_file_target)


def Environment( variabel, value):
   """
   Set a environment variable
   """
   os.environ[variabel] = value

def IncludePaths( paths):
   """
   Add 'extra' include paths 
   """
   makefile = caller()
   model.add_key_value( makefile.filename, 'include_paths', paths)

def LibraryPaths( paths):
   """
   Add 'extra' library paths 
   """
   makefile = caller()
   model.add_key_value( makefile.filename, 'library_paths', paths)

def Dependencies(target, dependencies):
   """
   Adding a possibility to setup a more 'soft' dependency
   """
   makefile = caller()

   if not isinstance( target, Target):
      target = model.register(name=target, filename=target, makefile=makefile.filename)

   if not isinstance( dependencies, list):
      raise SystemError("dependencies is " + str(dependencies) + " must be a list")

   dependency_list = []
   for dependency in dependencies:
      dependency_list.append( dependency)

   target.add_dependency( dependency_list)

def Build( filename):
   """
   Build a separate file
   """

   makefile = caller()
   if not os.path.isabs( filename):
      directory, dummy = os.path.split( makefile.filename)
      if directory:
         filename = directory + '/' + filename

   target = model.register(name=filename, filename=absolute_path( filename, makefile.filename), makefile = makefile.filename) 

   with open( filename) as file:
      importCode( file, filename, "makefile", 1)


   


