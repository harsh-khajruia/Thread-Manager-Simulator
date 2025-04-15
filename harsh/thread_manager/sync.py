import threading
import time
from typing import Any, Optional
from contextlib import contextmanager

class ThreadBarrier:
    """
    A synchronization primitive that allows multiple threads to wait for each other
    at a specific point in their execution.
    """
    
    def __init__(self, parties: int):
        """
        Initialize the barrier with the number of threads that must wait.
        
        Args:
            parties: Number of threads that must reach the barrier
        """
        self._parties = parties
        self._count = parties
        self._lock = threading.Lock()
        self._event = threading.Event()
        
    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all threads to reach the barrier.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if all threads reached the barrier, False if timeout occurred
        """
        with self._lock:
            self._count -= 1
            if self._count == 0:
                self._event.set()
                self._count = self._parties
                return True
                
        return self._event.wait(timeout=timeout)

class ThreadSemaphore:
    """
    A semaphore implementation that allows controlling access to a limited number of resources.
    """
    
    def __init__(self, value: int = 1):
        """
        Initialize the semaphore with a value.
        
        Args:
            value: Initial value of the semaphore (default: 1)
        """
        self._value = value
        self._lock = threading.Lock()
        self._event = threading.Event()
        
    @contextmanager
    def acquire(self, timeout: Optional[float] = None):
        """
        Acquire the semaphore, blocking if necessary.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            TimeoutError: If timeout occurs while waiting
        """
        if not self._acquire(timeout):
            raise TimeoutError("Failed to acquire semaphore")
        try:
            yield
        finally:
            self.release()
            
    def _acquire(self, timeout: Optional[float] = None) -> bool:
        """Internal method to acquire the semaphore"""
        with self._lock:
            if self._value > 0:
                self._value -= 1
                return True
                
        start_time = time.time()
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return False
                
            with self._lock:
                if self._value > 0:
                    self._value -= 1
                    return True
            time.sleep(0.1)
            
    def release(self):
        """Release the semaphore"""
        with self._lock:
            self._value += 1
            self._event.set()

class ThreadCountDownLatch:
    """
    A synchronization aid that allows one or more threads to wait until a set of
    operations being performed in other threads completes.
    """
    
    def __init__(self, count: int):
        """
        Initialize the countdown latch.
        
        Args:
            count: Number of times countDown() must be invoked before threads can pass through wait_for_zero()
        """
        self._count = count
        self._lock = threading.Lock()
        self._event = threading.Event()
        
    def count_down(self):
        """Decrement the count of the latch"""
        with self._lock:
            if self._count > 0:
                self._count -= 1
                if self._count == 0:
                    self._event.set()
                    
    def wait_for_zero(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the count to reach zero.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if count reached zero, False if timeout occurred
        """
        return self._event.wait(timeout=timeout) 