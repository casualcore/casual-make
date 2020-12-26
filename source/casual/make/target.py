import os

class Recipe( object):
   def __init__(self, function, arguments):
      self.function = function
      self.arguments = arguments

class Target(object):
   def __init__( self, name, filename = None, makefile = None):
      self.name = name
      self.makefile = None
      self.need_serial_execution = False
      self.dependency = []
      self.recipes = []

      directory = ''
      if makefile:
         directory, dummy = os.path.split( makefile)
         self.makefile = os.path.abspath( makefile)

      if filename:
         if not os.path.isabs( filename):
            self.filename = os.path.abspath( directory + '/' + filename)
         else:
            self.filename = filename
      else:
         self.filename = None

      self.execute = False

      if self.filename:
         if os.path.exists( self.filename):
            self.timestamp = os.path.getmtime( self.filename)
         else:
            self.timestamp = 0
            self.execute = True
      else:
         self.timestamp = 0

   def __eq__(self, other): 
        if not isinstance(other, Target):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and self.filename == other.filename

   def __repr__(self):
      if self.name:
         return self.name

   def __str__(self):
      if self.name:
         return self.name

   def __hash__(self):
      return hash((self.name, self.filename, self.makefile))

   def add_dependency( self, target):
      if isinstance( target, list):
         self.dependency.extend( target)
      else:
         self.dependency.append( target)

   def add_recipe( self, recipe):
      if isinstance( recipe, list):
         self.recipes.extend( recipe)
      else:
         self.recipes.append( recipe)

   def has_recipes( self):
      return len( self.recipes) > 0


