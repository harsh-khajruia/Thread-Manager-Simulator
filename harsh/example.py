import time
from thread_manager import ThreadManager
from thread_manager.sync import ThreadBarrier, ThreadSemaphore, ThreadCountDownLatch

def worker_task(worker_id, barrier, semaphore, latch):
    """Example worker task that demonstrates synchronization primitives"""
    print(f"Worker {worker_id} started")
    
    # Simulate some work
    time.sleep(1)
    
    # Use semaphore to control resource access
    with semaphore.acquire():
        print(f"Worker {worker_id} acquired semaphore")
        time.sleep(0.5)  # Simulate resource usage
        print(f"Worker {worker_id} released semaphore")
    
    # Wait at barrier for other workers
    print(f"Worker {worker_id} waiting at barrier")
    barrier.wait()
    print(f"Worker {worker_id} passed barrier")
    
    # Signal completion
    latch.count_down()
    print(f"Worker {worker_id} completed")
    
    return f"Result from worker {worker_id}"

def main():
    # Create synchronization primitives
    num_workers = 3
    barrier = ThreadBarrier(parties=num_workers)
    semaphore = ThreadSemaphore(value=2)  # Allow 2 workers to access resource at once
    latch = ThreadCountDownLatch(count=num_workers)
    
    # Create thread manager
    with ThreadManager(max_workers=num_workers) as manager:
        # Submit tasks
        thread_ids = []
        for i in range(num_workers):
            thread_id = manager.submit_task(worker_task, i, barrier, semaphore, latch)
            thread_ids.append(thread_id)
            print(f"Submitted task for worker {i}, thread_id: {thread_id}")
        
        # Wait for all tasks to complete
        print("Waiting for all workers to complete...")
        latch.wait_for_zero()
        
        # Get results from all threads
        for thread_id in thread_ids:
            thread_info = manager.get_thread_info(thread_id)
            print(f"Thread {thread_id} result: {thread_info.result}")
            print(f"Thread {thread_id} state: {thread_info.state}")

if __name__ == "__main__":
    main() 