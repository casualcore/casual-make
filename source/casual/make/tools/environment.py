import os

def __DEFAULT():
   return "1"

def set( parameter, value = __DEFAULT()):
   os.environ[parameter] = value

def get( parameter, value = None):
   if parameter in os.environ:
      return os.environ[parameter]
   elif isinstance( value, str):
      return value
   else:
      None