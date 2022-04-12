"""
Functions for running workers in pools of processes
"""

import datetime
import multiprocessing
import queue
import os
import signal
import threading
import time
import traceback
import types


class GenericWorker(object):
    """
    Abstract worker class
    """

    def __init__(self):
        raise NotImplementedError("Attempted to use an abstract GenericWorker")

    def __call__(self):
        raise NotImplementedError("Attempted to use an incomplete GenericWorker")



class WorkerProcess(object):
    """
    External process that runs GenericWorkers on a caller's behalf
    """

    #
    # Worker Runner
    #

    class WorkerRunner:
        """
        Run a GenericWorker in a thread
        """

        def __init__(self, identifier, worker, callback=lambda i, r, d: None):
            assert isinstance(worker, GenericWorker)
            assert callback is None or callable(callback)

            self.identifier = identifier
            self.worker = worker
            self.callback = callback
            self.thread = threading.Thread(target=self.__run)
            self.thread.setDaemon(True)
            self.thread.start()


        def __run(self):
            """
            Run the worker, calling back with what it returns or any exception
            it throws.
            """
            try:
                result = self.worker()
                diags = None
            except Exception as ex:
                result = ex
                diags = "\n".join(traceback.format_exception(type(ex), ex, ex.__traceback__))

            self.callback(self.identifier, result, diags)


        def join(self):
            """
            Wait for the work to finish
            """
            self.thread.join()


    #
    # Processor
    #

    #
    # Message types; for internal use only.
    #

    class _Message(object):
        """Abstract message"""
        pass


    # Caller -> Processor

    class _InboundMessage(_Message):
        """Abstract inbound message"""
        pass


    class _MessageNewTask(_InboundMessage):
        """Specifies a new task to be run"""
        def __init__(self, identifier, worker):
            assert isinstance(identifier, int) or isinstance(identifier, str)
            assert isinstance(worker, GenericWorker)
            self.identifier = identifier
            self.worker = worker

        def __str__(self):
            return "New Task '%s'" % (self.identifier)


    class _MessageFinish(_InboundMessage):
        """Finish all work and exit"""
        def __init__(self, wait=True):
            self.wait = wait

        def __str__(self):
            return "Finish, %s wait" % ("with" if self.wait else "without")


    class _MessageAction(_InboundMessage):
        """
        Take an action
        """
        def __init__(self,
                     action=lambda a: None,
                     args=()
                    ):
            self.action = action
            self.args = args

        def __str__(self):
            return "Action: %s %s" % (self.action, self.args)


    # Processor -> Caller

    class _OutboundMessage(_Message):
        """Abstract outbound message"""
        pass

    class _MessageDebug(_OutboundMessage):
        """Provides debug information"""
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message


    class _MessageExceptionReceived(_OutboundMessage):
        """Something on the external process side threw an exception"""

        def __init__(self, exception):
            assert isinstance(exception, Exception)
            self.exception = exception
            self.traceback = "\n".join(traceback.format_exception(
                type(exception), exception, exception.__traceback__))

        def __str__(self):
            return "Exception %s" % (self.exception)


    class _MessageResult(_OutboundMessage):
        """A task has finished and has a result to return"""
        def __init__(self, identifier, result, diags):
            self.identifier = identifier
            self.result = result
            self.diags = diags

        def __str__(self):
            return "Result from '%s': %s" % (self.identifier, self.result)


    class _MessageExited(_OutboundMessage):
        """The processor is exiting."""
        pass



    #
    # The Processor
    #


    def __init__(self,
                 name=None,
                 setup=lambda a: None,     # Global setup
                 setup_args=(),
                 teardown=lambda a: None,  # Global teardown
                 teardown_args=(),
                 load_limit=0,
                 idle_time=None,  # Seconds with no work before terminating
                 debug_callback=lambda s: None
                ):

        assert isinstance(load_limit, int), "Load limit must be an integer"
        assert load_limit >= 0, "Load limit must be zero or positive"
        assert idle_time is None \
            or isinstance(idle_time, float) \
            or isinstance(idle_time, int)

        self.created = datetime.datetime.now()

        self.name = name or self.__class__.__name__
        self.setup = setup
        self.setup_args = setup_args
        self.teardown = teardown
        self.teardown_args = teardown_args

        self.load_limit = load_limit
        self.idle_time = idle_time
        self.debug_callback = debug_callback

        self.lock = threading.Lock()

        # Outstanding callbacks by identifier
        self.callbacks = {}

        # Used by the relay to notify close() that all work is done.
        self.ended = threading.Condition()

        # Shared between both sides

        context = multiprocessing.get_context()

        self.to_proc = context.Queue()
        self.from_proc = context.Queue()

        # Caller-side thread to relay results

        self.relay = threading.Thread(name="%s Relay" % (name), target=self.__relay)
        self.relay.setDaemon(True)

        self.relayed_exception = None
        self.relayed_traceback = None

        # Worker-side process

        self.process = context.Process(
            target=self.__proc_run,
            args=(self.to_proc, self.from_proc,),
            daemon=True
        )

        self.running = True
        self.process.start()
        self.relay.start()


    def __debug(self, message):
        """Send a debug message"""
        self.from_proc.put(self._MessageDebug("%s: %s" % (self.name, message)))


    def __raise(self):
        """Raise an exception if one was stored by the process."""
        if self.relayed_exception is not None:
            raise self.relayed_exception


    def __len__(self):
        """
        Return the number of running workers
        """
        self.__raise()
        return len(self.callbacks)


    def is_running(self):
        """
        Determine if the processor is running
        """
        return self.running and self.process.is_alive() and self.relayed_exception is None


    def is_taking_work(self):
        """
        Determine if the process can take more workers
        """
        self.__raise()
        return self.is_running() and (self.load_limit == 0 or len(self.callbacks) < self.load_limit)


    def __relay(self):
        """
        Listen for returned results and call callbacks (Caller side)
        """

        try:

            while True:

                incoming = self.from_proc.get()

                if isinstance(incoming, self._MessageResult):

                    self.callbacks[incoming.identifier](
                        incoming.identifier,
                        incoming.result,
                        incoming.diags)
                    with self.lock:
                        del self.callbacks[incoming.identifier]

                elif isinstance(incoming, self._MessageDebug):

                    self.debug_callback(str(incoming))

                elif isinstance(incoming, self._MessageExited):

                    break

                elif isinstance(incoming, self._MessageExceptionReceived):

                    with self.lock:
                        self.running = False

                    # Do callbacks on anything outstanding
                    for identifier, callback in self.callbacks.items():
                        callback(identifier,
                                 RuntimeError("Processor failed: %s" % (incoming.exception)),
                                 diags=incoming.traceback)
                    self.callbacks.clear()

                else:

                    raise ValueError("Invalid message type '%s' received" % (type(incoming)))

        except Exception as ex:

            raise ex

        finally:

            # No matter what happens, force this to die.
            self.process.terminate()

            # Tell close() we're done if it's listening.
            self.ended.acquire()
            try:
                self.ended.notify_all()
            finally:
                self.ended.release()

            with self.lock:
                self.running = False



    def __proc_result_callback(self, identifier, result, diags):
        """
        Handle results provided by the WorkerRunner (External process side)
        """

        self.from_proc.put(self._MessageResult(identifier, result, diags))
        self.__debug("Sent result from %s" % (identifier))
        with self.proc_lock:
            del self.proc_workers[identifier]


    def __proc_run(self, to_proc, from_proc):
        """
        Run the processor (External process side)
        """

        try:

            self.__debug("Starting")

            # Run the setup code.  If that throws an exception, so be it.
            self.setup(self.setup_args)
            self.__debug("Setup succeeded")

            # These only exist on the process side

            self.proc_lock = threading.Lock()
            self.proc_workers = {}

            while True:

                # Get a message from the caller.  If we sit idle long
                # enough without work, behave as if we'd been told to
                # finish.

                try:
                    incoming = to_proc.get(timeout=self.idle_time)
                except queue.Empty:
                    if len(self.proc_workers) > 0:
                        continue
                    self.__debug("No work for %s seconds.  Terminating." % (self.idle_time))
                    # There should be no workers, but just in case...
                    incoming = self._MessageFinish(wait=True)

                self.__debug("Incoming message: %s" % (str(incoming)))

                if isinstance(incoming, self._MessageNewTask):

                    with self.proc_lock:
                        self.proc_workers[incoming.identifier] = self.WorkerRunner(
                            incoming.identifier,
                            incoming.worker,
                            callback=self.__proc_result_callback)

                elif isinstance(incoming, self._MessageAction):

                    self.__debug("Taking action: %s %s" % (incoming.action, incoming.args))
                    incoming.action(incoming.args)

                elif isinstance(incoming, self._MessageFinish):

                    self.__debug("Finishing")

                    self.running = False

                    if incoming.wait:
                        # Wait for all of the workers to finish
                        self.__debug("Waiting for %d workers to finish" % (len(self.proc_workers)))
                        for identifier, worker in list(self.proc_workers.items()):
                            self.__debug("%s: Waiting for completion" % (identifier))
                            worker.join()
                            self.__debug("%s: Completed" % (identifier))

                    # Run teardown.
                    self.teardown(self.teardown_args)
                    self.__debug("Tore down")
                    break

                else:
                    message = "Client sent invalid message type '%s' received" % (type(incoming))
                    self.__debug(message)
                    raise ValueError(message)


        except Exception as ex:

            self.__debug("Processor exception: %s" % (ex))
            from_proc.put(self._MessageExceptionReceived(ex))

        finally:

            # Let the caller know we're done
            self.__debug("Exiting")
            self.running = False
            from_proc.put(self._MessageExited())



    def __call__(self, identifier, worker, callback):
        """
        Add a new worker to the process (Caller side)
        """
        assert isinstance(identifier, int) or isinstance(identifier, str)
        assert isinstance(worker, GenericWorker)
        assert callback is None or callable(callback)

        self.__raise()

        with self.lock:

            if not self.running:
                raise RuntimeError("Processor is no longer running")

            if self.load_limit > 0 and len(self.callbacks) >= self.load_limit:
                raise RuntimeError("Processor has a full workload")

            self.callbacks[identifier] = callback
            self.to_proc.put(self._MessageNewTask(identifier, worker))


    def action(self, action=lambda a: None, args=None):
        """
        Take an action.
        """
        assert isinstance(action, types.LambdaType)

        with self.lock:
            self.to_proc.put(self._MessageAction(action, args))


    def close(self, wait=False):
        """
        Tell the external process to finish and exit.  (Caller side)
        """
        self.__raise()
        with self.lock:
            was_running = self.running
            self.running = False
        self.to_proc.put(self._MessageFinish(wait=wait))

        if wait and was_running and self.relayed_exception is None:
            self.ended.acquire()
            try:
                self.ended.wait()
            finally:
                self.ended.release()


    def terminate(self):
        """
        Hard kill the process (Caller side)
        """
        pid = self.process.pid
        # TODO: In Python 3.7 or later, use .close()
        self.process.terminate()
        # Multiprocessing will have just orphaned this without .kill()
        # and .close().
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # Not there?  Don't care.
        self.__raise()



class WorkerProcessPool(object):
    """
    A pool of worker processes selected based on number of jobs.
    """

    def __init__(self,
                 # WorkerProcess arguments
                 name=None,
                 setup=lambda: None,
                 setup_args=(),
                 teardown=lambda: None,
                 teardown_args=(),
                 load_limit=0,
                 idle_time=None,

                 # Common arguments
                 debug_callback=lambda s: None,

                 # WorkerProcessPool arguments
                 pool_size_limit=0
                ):

        self.processor_name = name
        self.processor_setup = setup
        self.processor_setup_args = setup_args
        self.processor_teardown = teardown
        self.processor_teardown_args = teardown_args
        self.processor_load_limit = load_limit
        self.processor_idle_time = idle_time

        self.debug_callback = debug_callback
        self.pool_size_limit = pool_size_limit

        self.lock = threading.Lock()
        self.running = True
        self.processor_number = 0
        self.processors = {}


    def __len__(self):
        return len(self.processors)


    def __debug(self, message):
        """
        Produce a debug message for whataver wants it.
        """
        self.debug_callback("%s: %s" % (self.processor_name, message))


    def groom(self):
        """
        Remove processors that are no longer running.
        """

        with self.lock:
            to_remove = []
            for name, processor in self.processors.items():
                if not processor.is_running():
                    to_remove.append((name, processor))

            for name, processor in to_remove:
                self.__debug("Terminating %s" % (name))
                self.processors[name].terminate()
                del self.processors[name]

            # If we hit an empty pool and the number has become
            # arbitrarily-large, reset it.
            if len(self.processors) == 0 and self.processor_number > 999999:
                self.__debug("Empty pool; resetting counter.")
                self.processor_number = 0


    def status(self):
        """
        Return a dictionary of the names of the processors and their loads
        """
        with self.lock:
            return dict([(name, len(processor)) for name, processor in self.processors.items()])



    def __call__(self, identifier, worker, callback):
        """
        Run a GenericWorker in the pool.  Call is identical to the same method
        in WorkerProcess.
        """

        with self.lock:
            if not self.running:
                raise RuntimeError("Pool is no longer running.")

        self.groom()

        with self.lock:

            # Select the youngest, least-loaded processor that's doing
            # something else, only selecting one with no load or
            # creating a new one as a last resort.  This will starve
            # unloaded processors of work as a way to encourage them
            # to shut down.

            lowest_load = self.processor_load_limit  # Can't be any more than this
            lowest_processor = None
            zero = None

            for name in sorted(self.processors,
                               key=lambda p: self.processors[p].created,
                               reverse=True):

                processor = self.processors[name]

                if not processor.is_taking_work():
                    continue

                load = len(processor)
                if load == 0:
                    # Keep this in reserve in case everyone else is full.
                    zero = processor
                elif load < lowest_load:
                    lowest_load = load
                    lowest_processor = processor

            use = lowest_processor or zero

            # If no processor was found, spin up a new one.

            if use is None:

                if self.pool_size_limit and len(self.processors) >= self.pool_size_limit:
                    raise RuntimeError("Pool is completely full.")

                self.processor_number += 1
                name = "%s-%d" % (self.processor_name, self.processor_number)
                self.__debug("Starting new processor %s" % (name))
                use = WorkerProcess(
                    name=name,
                    setup=self.processor_setup,
                    setup_args=self.processor_setup_args,
                    teardown=self.processor_teardown,
                    teardown_args=self.processor_teardown_args,
                    load_limit=self.processor_load_limit,
                    idle_time=self.processor_idle_time,
                    debug_callback=self.debug_callback,
                )
                self.processors[name] = use

            use(identifier, worker, callback)


    def action(self, action=lambda a: None, args=None):
        """
        Take an action on all processors in the pool.
        """
        assert isinstance(action, types.LambdaType)

        with self.lock:
            self.__debug("Taking action on all processors in pool:")
            for name, processor in self.processors.items():
                self.__debug("  %s" % (name))
                processor.action(action, args)


    def close(self, wait=False, terminate=False):
        """
        Close out the pool.
        """

        with self.lock:
            self.running = False

        # Beyond this point, calls to __call__() will fail, so there's
        # no need to continue holding the lock.

        self.groom()

        self.__debug("Closing the pool.")

        with self.lock:
            for name in self.processors:
                if terminate:
                    self.__debug("Terminating %s" % (name))
                    self.processors[name].terminate()
                else:
                    self.__debug("Closing %s" % (name))
                    self.processors[name].close(wait=wait)

                del self.processors[name]
