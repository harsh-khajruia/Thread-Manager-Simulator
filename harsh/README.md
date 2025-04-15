# Thread Manager

A high-performance thread management library for Python that supports efficient creation, synchronization, and termination of threads. The library is designed to handle thousands of threads concurrently and is suitable for high-performance computing applications.

## Features

- Efficient thread management with thread pooling
- Thread state tracking and monitoring
- Synchronization primitives (Barrier, Semaphore, CountDownLatch)
- Context manager support for resource cleanup
- Timeout support for all blocking operations
- Thread-safe operations with proper locking mechanisms
- Interactive GUI for thread visualization and control

## Installation

```bash
pip install -r requirements.txt
```

## Usage Examples

### Basic Thread Management

```python
from thread_manager import ThreadManager

def task(x):
    return x * x

# Create a thread manager
with ThreadManager(max_workers=4) as manager:
    # Submit tasks
    thread_id1 = manager.submit_task(task, 5)
    thread_id2 = manager.submit_task(task, 10)

    # Wait for specific thread
    manager.wait_for_thread(thread_id1)

    # Get thread information
    thread_info = manager.get_thread_info(thread_id1)
    print(f"Result: {thread_info.result}")  # Output: 25
```

### Using Synchronization Primitives

```python
from thread_manager import ThreadManager
from thread_manager.sync import ThreadBarrier, ThreadSemaphore, ThreadCountDownLatch

def worker(barrier, semaphore, latch):
    with semaphore.acquire():  # Control resource access
        # Do some work
        barrier.wait()  # Wait for other threads
        latch.count_down()  # Signal completion

# Create synchronization primitives
barrier = ThreadBarrier(parties=3)
semaphore = ThreadSemaphore(value=2)
latch = ThreadCountDownLatch(count=3)

# Create thread manager
with ThreadManager(max_workers=3) as manager:
    # Submit tasks
    for _ in range(3):
        manager.submit_task(worker, barrier, semaphore, latch)

    # Wait for all tasks to complete
    latch.wait_for_zero()
```

### Using the GUI Application

The library includes a GUI application for visualizing and controlling threads:

```bash
python thread_manager_gui.py
```

#### GUI Features:

1. **Thread Control Panel**:

   - Set the number of tasks to create (1-10)
   - Choose task type:
     - `random`: Variable execution time (0.5-1.5s per step)
     - `sequential`: Fixed execution time (0.5s per step)
     - `cpu_intensive`: CPU-bound workload (2.0s per step with calculations)
   - Start, stop, and clear controls

2. **Statistics Panel**:

   - Real-time counts of active, completed, and error threads
   - Total thread count

3. **Thread Status Panel**:

   - Color-coded thread states:
     - Gray: IDLE
     - Yellow: RUNNING
     - Green: TERMINATED
     - Red: ERROR
   - Progress tracking (0-100%)
   - Result display

4. **Log Panel**:
   - Timestamped activity log
   - Task progress updates
   - Error reporting

## API Reference

### ThreadManager

- `__init__(max_workers=None, name_prefix="ThreadManager")`: Initialize the thread manager
- `submit_task(task, *args, **kwargs)`: Submit a task for execution
- `get_thread_info(thread_id)`: Get information about a specific thread
- `get_active_threads()`: Get information about all active threads
- `wait_for_thread(thread_id, timeout=None)`: Wait for a specific thread to complete
- `shutdown(wait=True)`: Shutdown the thread manager

### ThreadBarrier

- `__init__(parties)`: Initialize the barrier
- `wait(timeout=None)`: Wait for all threads to reach the barrier

### ThreadSemaphore

- `__init__(value=1)`: Initialize the semaphore
- `acquire(timeout=None)`: Acquire the semaphore
- `release()`: Release the semaphore

### ThreadCountDownLatch

- `__init__(count)`: Initialize the countdown latch
- `count_down()`: Decrement the count
- `wait_for_zero(timeout=None)`: Wait for the count to reach zero

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
