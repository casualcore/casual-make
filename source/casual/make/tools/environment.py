import os

def __DEFAULT():
   return "1"

def set( parameter, value = __DEFAULT()):
   os.environ[parameter] = value

def get( parameter):
   if parameter in os.environ:
      return os.environ[parameter]
   else:
      None