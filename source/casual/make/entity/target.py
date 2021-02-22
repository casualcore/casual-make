import os

class Recipe( object):
   def __init__(self, function, arguments):
      self.function = function
      self._arguments = arguments

   def arguments(self):
      return self._arguments

class Target(object):
   def __init__( self, name, filename = None, makefile = None):
      self._name = name
      self._makefile = None
      self._execute = False
      self._serial = False
      self._dependency = []
      self._recipe = []
      self._max = None
      self._filename = None
      self._timestamp = None


      directory = ''
      if makefile:
         directory, dummy = os.path.split( makefile)
         self._makefile = os.path.abspath( makefile)

      if filename:
         if not os.path.isabs( filename):
            self._filename = os.path.abspath( directory + '/' + filename)
         else:
            self._filename = filename

      if self._filename:
         if os.path.exists( self._filename):
            self._timestamp = os.path.getmtime( self._filename)
         else:
            self._timestamp = 0
            self._execute = True
      else:
         self._timestamp = 0

      self.hash = hash((self._name, self._filename, self._makefile))

   def name(self, name = None):
      if not name:
         return self._name

      self._name = name

      return self._name

   def makefile(self, makefile = None):
      if not makefile:
         return self._makefile
      
      self._makefile = makefile

      return self._makefile

   def max(self, max = None):

      if not max:
         return self._max

      self._max = max

      return self._max

   def dependency(self, dependency = None):
      if not dependency:
         return self._dependency

      self._dependency = dependency
      return self._dependency

   def recipe( self, recipe = None):
      if not recipe:
         return self._recipe

      self._recipe = recipe
      return self._recipe

   def filename( self, filename = None):
      if not filename:
         return self._filename

      self._filename = filename
      return self._filename

   def timestamp( self, timestamp = None):
      if not timestamp:
         return self._timestamp

      self._timestamp = timestamp
      return self._timestamp


   def __eq__(self, other): 
        if not isinstance(other, Target):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.hash == other.hash
        
   def __repr__(self):
      if self._name:
         return self._name

   def __str__(self):
      if self._name:
         return self._name

   def __hash__(self):
      return self.hash

   def add_dependency( self, target):
      if not target:
         return self

      if isinstance( target, list):
         self._dependency.extend( target)
      else:
         self._dependency.append( target)

      return self

   def add_recipe( self, recipe):
      if not recipe:
         return self
         
      if isinstance( recipe, list):
         self._recipe.extend( recipe)
      else:
         self._recipe.append( recipe)

      return self

   def has_recipes( self):
      return self._recipe

   def execute( self, execute = None):
      if not execute:
         return self._execute
      
      self._execute = execute
      return self

   def serial( self, serial = None):
      if not serial:
         return self._serial

      self._serial = serial
      return self

