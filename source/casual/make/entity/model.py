import inspect
import pprint
import os
import time
import sys

from casual.make.entity.target import Target
from casual.make.tools.executor import importCode
import casual.make.tools.environment as environment


# globals
class Store( object):
   def __init__(self):
      # actual model
      self.m_model = { 'key_value' : {}}
      # target cache
      self.m_target_cache = {}
      self.m_analyze_cache = {}

   def model(self):
      return self.m_model

   def target_cache(self):
      return self.m_target_cache

   def analyze_cache(self):
      return self.m_analyze_cache

   def get(self, name, filename = None, paths = None):
      """
      Fetch target from model
      """
      # First - exact match
      if name and filename and name in self.m_target_cache and filename in self.m_target_cache[name]:
         return self.m_target_cache[name][filename]
      # Second - match by correct path
      elif paths:
         for path in paths:
            for fname in self.m_target_cache[name]:
               if path in fname:
                  return self.m_target_cache[name][fname]
      # Third - correct name - no other options - pick first
      elif name in self.m_target_cache and not filename:
         for f in self.m_target_cache[name]:
            return self.m_target_cache[name][f]
      return None

   def register(self, name, filename = None, makefile = None):
      """
      Create and register target in model
      """
      if isinstance( name, Target):
         target = self.get( name.name(), name.filename())
         if target:
            return target
         self.m_target_cache[name.name()][name.filename()] = name
         return name
      else:
         target = self.get( name, filename)
         if target:
            return target
         else:
            if name not in self.m_target_cache:
               self.m_target_cache[name] = {}
            self.m_target_cache[name][filename] = Target( name, filename, makefile)
            return self.m_target_cache[name][filename]

# instance of the global store
store = Store()

force_execution = False

def register( name, filename = None, makefile = None):

   if not name: raise SyntaxError( "Can't create target from None values")
   return store.register( name, filename, makefile)

def get( name, filename = None, paths = None):
   return store.get( name)

def dump_model():
   pprint.pprint( store.model())

def dump_target_cache():
   pprint.pprint( store.target_cache())

def dump_analyze_cache():
   pprint.pprint( store.analyze_cache())


def add_key_value( makefile, key, value):
   """
   Add key, value in model
   """
   if makefile not in store.model()['key_value']:
      store.model()['key_value'][makefile] = {}
   store.model()['key_value'][makefile][key] = value

def get_value( makefile, key):
   """
   Get value with key from model 
   """
   if makefile in store.model()['key_value'] and key in store.model()['key_value'][makefile]:
      return store.model()['key_value'][makefile][key]
   else:
      return None

def make_absolute_path( paths, directory):
   """
   Normalize path in path list
   """
   reply = []
   for path in paths:
      if os.path.isabs(path):
         reply.append( path)
      else:
         reply.append( os.path.abspath( directory + '/' + path))
   return reply

def include_paths( makefile):
   value = get_value( makefile, 'include_paths')
   return value if value else []

def library_paths( makefile):
   value = get_value( makefile, 'library_paths')
   directory, dummy = os.path.split( makefile)
   return make_absolute_path( value, directory) if value else []

def construct_dependency_tree( target):
   """
   Construcs a depedency tree in the view of the target_rhs
   """
   if not isinstance( target, Target):
      target = store.get( target)

   global force_execution
   force_execution = True if environment.get("CASUAL_MAKE_FORCE_EXECUTION") else False
   
   return analyze_dependency_tree( target)

def calculate_max_timestamp( target):
   """
   Retrive max timestamp
   """
   if not target.dependency(): return 0.0
   if target.max(): return target.max()

   value = max( target.dependency(), key=lambda item: item.timestamp()).timestamp()
   return target.max( value)

def analyze_dependency_tree( target):
   """
   Analyzing tree for actions to take
   Returns: is action required? True/False
   """
   if target in store.analyze_cache():
      return store.analyze_cache()[target]

   if not target:
      raise SyntaxError('target is None')

   if not target.dependency():
      store.analyze_cache()[target] = target.execute()
      return target.execute()
   else:
      action_needed = False
      current_target = target

      for child_target in current_target.dependency():

         action_required = analyze_dependency_tree( child_target)

         if current_target:

            if action_required or force_execution:

               # The depedency steps is already evalutated to be run
               # So we need to run this one too.
               current_target.execute(True)
               action_needed = True
               continue

            timestamp = current_target.timestamp()
            if current_target.filename() and not timestamp:

               # No timestamp, means no file.
               # Need to run this step
               current_target.execute(True)
               action_needed = True
               continue
               
            else:
               max_timestamp = calculate_max_timestamp( current_target)

               if current_target.filename() and timestamp < max_timestamp:
                  # The dependency files is newer.
                  # Need to run this step
                  current_target.execute(True)
                  action_needed = True
                  continue

   store.analyze_cache()[target] = action_needed
   return action_needed

def construct_action_list( target):
   """
   Construct a action list based on the dependency tree
   """


   def flatten( target):
      """
      flatten the tree, and prodcue a 'raw' result
      """

      def dependencies_has_recipe( target):
         stack = []
         stack.extend( target.dependency())
         while stack:
            next = stack.pop()
            if next.execute() and next.has_recipes(): return True
            if next.dependency(): stack.extend( next.dependency())
         return False

      stack = [ ( 0, target)]
      result = []
      leafs = []
      
      while stack:
         ( index, next) = stack.pop()

         while len( result) <= index:
            result.append( [])
         
         if dependencies_has_recipe( next):
            if next.execute() and next.has_recipes():
               result[ index].append( next)
            
            for item in next.dependency():
               stack.append( ( index + 1, item))
         elif next.execute() and next.has_recipes():
            # no dependencies with recipes, hence a 'leaf'
            leafs.append( next)

      # add the (unique) leafs
      result.append( list( dict.fromkeys( leafs)))
      return result


   def normalize( levels):
      """
      normalizes the action list, returns unique actions 
      """

      def action_exists( action, result):
         for item in result:
            hashed = [h.hash for h in item]
            if action.hash in hashed: return True
         return False

      result = []
      for level in reversed( levels):
         prospect = [ action for action in level if not action_exists( action, result)]
         if prospect: result.append( list( dict.fromkeys( prospect)))

      return result

   return normalize( flatten( target))

def build():
   """
   Build the model from a file
   """

   # Open the default name 'makefile.cmk'
   # Only supported option right now
   with open("makefile.cmk") as file:
      importCode( file, "makefile.cmk", "makefile", 1)
