import threading
import queue
import logging
import time
from typing import Callable, Any, Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum, auto

class ThreadState(Enum):
    """Thread states for tracking thread lifecycle"""
    IDLE = auto()
    RUNNING = auto()
    TERMINATED = auto()
    ERROR = auto()

@dataclass
class ThreadInfo:
    """Information about a managed thread"""
    thread_id: int
    state: ThreadState
    task: Optional[Callable] = None
    args: tuple = ()
    kwargs: dict = None
    result: Any = None
    error: Optional[Exception] = None

class ThreadManager:
    """
    A high-performance thread management system that supports efficient creation,
    synchronization, and termination of threads.
    """
    
    def __init__(self, max_workers: int = None, name_prefix: str = "ThreadManager"):
        """
        Initialize the thread manager.
        
        Args:
            max_workers: Maximum number of threads to create. If None, it will be
                        determined based on CPU count.
            name_prefix: Prefix for thread names
        """
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=name_prefix)
        self._threads: Dict[int, ThreadInfo] = {}
        self._lock = threading.Lock()
        self._task_queue = queue.Queue()
        self._logger = logging.getLogger(__name__)
        self._running = True
        
    def submit_task(self, task: Callable, *args, **kwargs) -> int:
        """
        Submit a task to be executed by a thread.
        
        Args:
            task: The callable to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
            
        Returns:
            int: Thread ID assigned to the task
        """
        with self._lock:
            thread_id = len(self._threads)
            thread_info = ThreadInfo(
                thread_id=thread_id,
                state=ThreadState.IDLE,
                task=task,
                args=args,
                kwargs=kwargs or {}
            )
            self._threads[thread_id] = thread_info
            
        future = self._executor.submit(self._execute_task, thread_id)
        future.add_done_callback(lambda f: self._handle_task_completion(thread_id, f))
        
        return thread_id
    
    def _execute_task(self, thread_id: int) -> Any:
        """Execute the task and update thread state"""
        thread_info = self._threads[thread_id]
        thread_info.state = ThreadState.RUNNING
        
        try:
            result = thread_info.task(*thread_info.args, **thread_info.kwargs)
            return result
        except Exception as e:
            self._logger.error(f"Error in thread {thread_id}: {str(e)}")
            thread_info.error = e
            thread_info.state = ThreadState.ERROR
            raise
    
    def _handle_task_completion(self, thread_id: int, future):
        """Handle task completion and update thread state"""
        thread_info = self._threads[thread_id]
        try:
            thread_info.result = future.result()
            thread_info.state = ThreadState.TERMINATED
        except Exception as e:
            thread_info.error = e
            thread_info.state = ThreadState.ERROR
    
    def get_thread_info(self, thread_id: int) -> Optional[ThreadInfo]:
        """Get information about a specific thread"""
        return self._threads.get(thread_id)
    
    def get_active_threads(self) -> List[ThreadInfo]:
        """Get information about all active threads"""
        return [info for info in self._threads.values() if info.state == ThreadState.RUNNING]
    
    def wait_for_thread(self, thread_id: int, timeout: Optional[float] = None) -> bool:
        """
        Wait for a specific thread to complete.
        
        Args:
            thread_id: The ID of the thread to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if thread completed, False if timeout occurred
        """
        if thread_id not in self._threads:
            raise ValueError(f"Thread {thread_id} not found")
            
        start_time = time.time()
        while self._threads[thread_id].state == ThreadState.RUNNING:
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        return True
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the thread manager and release resources.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        self._running = False
        self._executor.shutdown(wait=wait)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown() 