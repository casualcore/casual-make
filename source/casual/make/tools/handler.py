from multiprocessing import Queue, Process
from queue import Empty

import multiprocessing as mp
import signal
import casual.make.entity.recipe as recipe
import sys
import os
from time import sleep


   

def need_serial_execution( action_list):
   """
   Find out if any item in list require serial handling
   """
   if os.getenv("CASUAL_SERIAL_EXECUTION"):
      return True
      
   for item in action_list:
      if item.need_serial_execution:
         return True
   return False


def worker( input, output):
   try:
      while True:
         item = input.get(True, 1)

         try:
            recipe.dispatch( item)
            output.put( ( item, True))
         except SystemError as ex:
            sys.stderr.write( '\nprocessed makefile: ' + str(item.makefile) + '\n')
            sys.stderr.write( 'processed filename: ' + str(item.filename) + '\n')
            sys.stderr.write( str(ex))
            output.put( ( item, False))
         except PermissionError as ex:
            sys.stderr.write( str(item) + '\n')
            sys.stderr.write( str(ex) + '\n')
            output.put( ( item, False))

   except Empty:
      pass

def terminate_children( process):
   for p in process:
      if p.is_alive():
         p.join()


def serial( actions):
   """
   Handle actions in serial
   """
   for item in actions:
      try:
         recipe.dispatch( item)
      except SystemError as ex:
         sys.stderr.write( '\nprocessed makefile: ' + str(item.makefile) + '\n')
         sys.stderr.write( 'processed filename: ' + str(item.filename) + '\n')
         raise

class Handler:
   def __init__( self):
      self.processes = []

      # Create queues
      self.task_queue = Queue()
      self.reply_queue = Queue()

   def __enter__( self):
      for dummy in range( mp.cpu_count()):
         process = Process( target = worker, args=( self.task_queue, self.reply_queue))
         process.daemon = True
         process.start()
         self.processes.append( process)
      return self

   def __exit__( self, exc_type, exc_value, traceback):
      self.__empty()

   def __parallel( self, actions):
      """
      Handle actions in parallel
      """

      try:
         # Submit actions
         for action in actions:
            self.task_queue.put( action, True)

         while actions:
            (action, ok) = self.reply_queue.get( True)
            actions.remove( action)
            if not ok:
               raise SystemError("error building...")

      except KeyboardInterrupt:
         print("\nCaught KeyboardInterrupt, terminating workers")
         self.__empty()
         #terminate_children( process)
         raise SystemError("aborting...")
      except:
         #print ("cleaning queues")
         self.__empty()
         raise

   def __empty( self):
      self.task_queue.cancel_join_thread()
      while not self.task_queue.empty():
         try:
            self.task_queue.get_nowait()
         except:
            pass

      self.reply_queue.cancel_join_thread()
      while not self.reply_queue.empty():
         try:
            self.reply_queue.get_nowait()
         except:
            pass


   def handle( self, actions):
      """
      Handle the action list in parallel or in serial
      """

      if need_serial_execution( actions):
         serial( actions)
      else:
         self.__parallel( actions)

