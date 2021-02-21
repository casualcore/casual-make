import inspect
import os

import casual.make.entity.model as model
import casual.make.entity.recipe as recipe
import casual.make.tools.environment as environment

from casual.make.entity.target import Target, Recipe
from casual.make.tools.executor import importCode

import importlib
compiler_handler = environment.get("CASUAL_MAKE_COMPILER_HANDLER")
selector = importlib.import_module( compiler_handler)

#
# global setup for operations
#
compile_target = model.register( 'compile')
link_library_target = model.register( 'link-library')
link_archive_target = model.register( 'link-archive')
link_executable_target = model.register( 'link-executable')
link_unittest_target = model.register( 'link-unittest')
link_target = model.register( 'link').add_dependency( 
   [
      link_library_target, 
      link_archive_target, 
      link_executable_target, 
      link_unittest_target
   ]
)

test_target = model.register('test').execute(True).serial(True)
clean_target = model.register( 'clean')
install_target = model.register('install').serial(True)

#
# Helpers
#
def caller():

   name = inspect.getouterframes( inspect.currentframe())[2][1]
   path = os.path.abspath( name)
   return model.register(name=path, filename=path, makefile = path) 

def absolute_path( filename, makefile):

   if os.path.isabs( filename): return filename
   directory, dummy = os.path.split( makefile)
   assembled = os.path.join( directory, filename)
   return os.path.abspath( assembled)

def normalize_library_target( libs, paths = None):
   reply = []
   for lib in libs:
      if not isinstance( lib, Target):
         target = model.get( lib, paths)
         lib = target if target else model.register( lib)
      reply.append( lib)
   return reply

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
            abs_path = os.path.abspath( os.path.join(context_directory, filename))
         item = model.store.register( abs_path, abs_path, makefile)

         reply.append( item)
      return reply
   else:
      return []

def make_clean_target( targets, makefile):
   """
   helper for very frequent operation
   """
   for target in targets:
      clean_target.add_dependency(
         model.register(
            'clean_' + target.name(), makefile = makefile.filename())
         .add_recipe( 
            Recipe( recipe.clean, {'filename' : target, 'makefile': makefile.filename()}))
         .execute(True)
      )  

#
# Main DSL
#
def Compile( sourcefile, objectfile = None, directive = []):
   """
   Compile code to object files
   """
   makefile = caller()

   if not objectfile: objectfile = selector.make_objectname( sourcefile)

   dependencyfile = selector.make_dependencyfilename( objectfile)
   dependencyfile_target = model.register(name=dependencyfile, filename=absolute_path( dependencyfile, makefile.filename()), makefile = makefile.filename()) 
   object_dependencies = includes( dependencyfile_target.filename(), makefile = makefile.filename())
   source_target = model.register(name=sourcefile, filename=absolute_path(sourcefile, makefile.filename()), makefile = makefile.filename())
   
   dependencyfile_target.add_dependency( source_target)

   # no dependency file - add at least source file
   if not object_dependencies: object_dependencies = [source_target]
   
   # add dependencyfile_target to dependency
   object_dependencies.append( dependencyfile_target)
   # add makefile to dependency
   object_dependencies.append( makefile)

   # register the objectfile in module
   object_target = model.register(name=objectfile, filename=absolute_path(objectfile, makefile.filename()), makefile = makefile.filename())
   
   arguments = { 
      'destination' : object_target, 
      'dependencyfile' :  dependencyfile,
      'source' : source_target, 
      'include_paths' : model.include_paths( makefile.filename()),
      'directive' : directive
      }

   object_target.add_recipe( 
      Recipe( recipe.execute_dependency_generation, arguments)
   ).add_recipe( 
      Recipe( recipe.compile, arguments)
   ).add_dependency( object_dependencies)

   compile_target.add_dependency( object_target)

   make_clean_target( [ object_target, dependencyfile_target], makefile)

   return object_target

def LinkLibrary( destination, objects, libs):
   """
   Link object files to shared objects library
   """
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename())
   name = os.path.basename(destination)
   full_library_name = selector.expanded_library_name( destination, directory)
   library_target = model.register(name=name, filename=full_library_name, makefile = makefile.filename())

   library_paths = model.library_paths( makefile.filename())
   normalized_library_targets = normalize_library_target( libs, paths = library_paths)
   arguments = {
      'destination' : library_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   library_target.add_recipe( 
      Recipe( recipe.link_library, arguments)
   ).add_dependency( objects + normalized_library_targets)

   link_library_target.add_dependency( [library_target, makefile])

   make_clean_target( [library_target], makefile)

   return library_target

def LinkArchive( destination, objects):
   """
   Link object files to archive
   """
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename())
   name=os.path.basename(destination)

   full_archive_name = selector.expanded_archive_name( destination, directory)
   archive_target = model.register(name=name, filename=full_archive_name, makefile = makefile.filename())
   arguments = {
      'destination' : archive_target, 
      'objects' : objects
      }

   archive_target.add_recipe ( 
      Recipe( recipe.link_archive, arguments)
   ).add_dependency( objects)

   link_archive_target.add_dependency( [archive_target, makefile])

   make_clean_target( [archive_target], makefile)

   return archive_target

def LinkExecutable( destination, objects, libs):
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename())

   full_executable_name = selector.expanded_executable_name(destination, directory)
   executable_target = model.register( full_executable_name, full_executable_name, makefile = makefile.filename())
   library_paths = model.library_paths( makefile.filename())
   normalized_library_targets = normalize_library_target( libs, library_paths)
   arguments = {
      'destination' : executable_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   executable_target.add_recipe( 
      Recipe( recipe.link_executable, arguments)
   ).add_dependency( objects + normalized_library_targets)

   link_executable_target.add_dependency( [executable_target, makefile])

   make_clean_target( [executable_target], makefile)

   return executable_target

def LinkUnittest( destination, objects, libs):
   
   makefile = caller()
   directory, dummy = os.path.split( makefile.filename())

   full_executable_name = selector.expanded_executable_name(destination, directory)
   executable_target = model.register( full_executable_name, full_executable_name, makefile = makefile.filename())
   library_paths = model.library_paths( makefile.filename())
   normalized_library_targets = normalize_library_target( libs, library_paths) + normalize_library_target([ 'gtest', 'gtest_main' ])
   arguments = {
      'destination' : executable_target, 
      'objects' : objects, 
      'libraries': normalized_library_targets, 
      'library_paths': library_paths
      }

   executable_target.add_recipe( 
      Recipe( recipe.link_unittest, arguments)
   ).add_dependency( objects + normalized_library_targets)

   link_unittest_target.add_dependency( [executable_target, makefile])

   make_clean_target( [executable_target], makefile)

   test_executable_target = model.register( 
      "test-" + destination, destination, makefile = makefile.filename()
   ).add_recipe( 
      Recipe( 
         recipe.test,
         {
            'destination' : executable_target,
            'library_paths': library_paths
         }
      ) 
   ).execute(True).serial(True)

   test_executable_target.add_dependency( executable_target)
   test_target.add_dependency( test_executable_target)

   return executable_target

def Install( source, path):
   
   if not source: return None
   if not isinstance( source, list): source = [source]

   makefile = caller()

   for item in source:
      if isinstance( item, tuple):
         install_file_target = model.register( 'install_' + item[0], makefile = makefile.filename())
         dependency_target = model.get( item[0])
         if not dependency_target:
            filename = os.path.abspath( os.path.dirname( makefile.filename()) + '/' + item[0])
            dependency_target = model.register( item[0], filename, makefile = makefile.filename())
         install_file_target.add_dependency( dependency_target).execute(True).serial(True)
         arguments = {
            'source' : dependency_target.filename(), 
            'path' : path + '/' + item[1]
         }
         install_file_target.add_recipe( Recipe( recipe.install, arguments))
         install_target.add_dependency( install_file_target)
      elif isinstance( item, model.Target):
         install_file_target = model.register( 'install_' + item.name(), makefile = makefile.filename())
         dependency_target = item
         install_file_target.add_dependency( dependency_target).execute(True).serial(True)
         arguments = {
            'source' : dependency_target.filename(), 
            'path' : path
         }
         install_file_target.add_recipe( Recipe( recipe.install, arguments))
         install_target.add_dependency( install_file_target)
      else:
         install_file_target = model.register('install_' + item, makefile = makefile.filename())
         dependency_target = model.get( item)
         if not dependency_target:
            filename = os.path.abspath( os.path.dirname( makefile.filename()) + '/' + item)
            dependency_target = model.register( item, filename, makefile = makefile.filename())
         install_file_target.add_dependency( dependency_target).execute(True).serial(True)
         arguments = {
            'source' : dependency_target.filename(), 
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
   model.add_key_value( caller().filename(), 'include_paths', paths)

def LibraryPaths( paths):
   """
   Add 'extra' library paths 
   """
   model.add_key_value( caller().filename(), 'library_paths', paths)

def Dependencies(target, dependencies):
   """
   Adding a possibility to setup a more 'soft' dependency
   """
   if not isinstance( target, Target):
      target = model.register(name=target, filename=target, makefile=caller().filename())

   if not isinstance( dependencies, list):
      raise SystemError("dependencies is " + str(dependencies) + " must be a list")

   target.add_dependency( dependencies)

def Build( filename):
   """
   Build a separate file
   """

   makefile = caller()
   if not os.path.isabs( filename):
      directory, dummy = os.path.split( makefile.filename())
      if directory: filename = os.path.join( directory, filename)

   target = model.register(name=filename, filename=absolute_path( filename, makefile.filename()), makefile = makefile.filename()) 

   with open( filename) as file:
      importCode( file, filename, "makefile", 1)


   


