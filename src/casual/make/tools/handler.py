from multiprocessing import Queue, Process
from queue import Empty

import multiprocessing as mp
import casual.make.entity.recipe as recipe
import casual.make.entity.state as state

import casual.make.tools.output as out
import sys
import os


def worker(input, output):
    while True:
        try:
            item = input.get(True, 1)

            if item == terminate_process():
                break

            recipe.dispatch(item)
            output.put((item, True))
        except SystemError as ex:
            if state.settings.verbose():
                out.error('\nprocessed makefile: ' + str(item.makefile))
            if state.settings.verbose():
                out.error('processed filename: ' + str(item.filename))
            if not state.settings.ignore_errors():
                out.error(str(ex))
            output.put((item, False))
            break
        except PermissionError as ex:
            out.error(str(item))
            out.error(ex)
            output.put((item, False))
            break
        except Empty:
            pass


def terminate_children(process):
    for p in process:
        if p.is_alive():
            p.join()


def terminate_process():
    return "terminate_process"


def serial(actions):
    """
    Handle actions in serial
    """
    actions.sort(key=lambda x: x._targetid)
    for item in actions:
        try:
            recipe.dispatch(item)
        except SystemError as ex:
            if state.settings.verbose():
                out.error('\nprocessed makefile: ' + str(item.makefile))
            if state.settings.verbose():
                out.error('processed filename: ' + str(item.filename))
            if not state.settings.ignore_errors():
                raise


class Handler:
    def __init__(self):
        self.processes = []

        # Create queues
        self.task_queue = Queue()
        self.reply_queue = Queue()

    def __enter__(self):
        for dummy in range(mp.cpu_count()):
            process = Process(target=worker, args=(
                self.task_queue, self.reply_queue))
            process.daemon = True
            process.start()
            self.processes.append(process)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__empty()

    def __parallel(self, actions):
        """
        Handle actions in parallel
        """
        actions.sort(key=lambda x: x._targetid)

        try:
            # Submit actions
            for action in actions:
                self.task_queue.put(action, True)

            while actions:
                (action, ok) = self.reply_queue.get(True)

                actions.remove(action)
                if not ok and not state.settings.ignore_errors():
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

    def __empty(self):
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

        for dummy in range(mp.cpu_count()):
            self.task_queue.put(terminate_process(), True)

    def handle(self, actions):
        """
        Handle the action list in parallel or in serial
        """
        def has_serial(item):
            return item.serial()

        def has_parallel(item):
            return not has_serial(item)

        if state.settings.serial():
            serial(actions)
        else:
            serial_actions = list(filter(has_serial, actions))

            parallel_actions = list(filter(has_parallel, actions))

            self.__parallel(parallel_actions)
            serial(serial_actions)
