import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import random
from threading import Thread
from queue import Queue
from thread_manager import ThreadManager
from thread_manager.sync import ThreadBarrier, ThreadSemaphore, ThreadCountDownLatch

class ThreadState:
    """Visual properties for different thread states"""
    COLORS = {
        'IDLE': ('#E8E8E8', '#000000'),      # Light gray background, black text
        'RUNNING': ('#FFF7E6', '#996600'),    # Light yellow background, brown text
        'TERMINATED': ('#E6FFE6', '#006600'), # Light green background, dark green text
        'ERROR': ('#FFE6E6', '#CC0000')       # Light red background, dark red text
    }

class ThreadManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thread Manager GUI")
        self.root.geometry("1000x700")
        
        # Set theme
        style = ttk.Style()
        style.theme_use('clam')  # Use 'clam' theme for better control over colors
        
        # Initialize thread manager
        self.thread_manager = ThreadManager(max_workers=10)
        self.update_queue = Queue()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start update thread
        self.update_thread = Thread(target=self.update_gui, daemon=True)
        self.update_thread.start()
        
    def create_widgets(self):
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Thread control panel
        control_frame = ttk.LabelFrame(main_container, text="Thread Control", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Task controls
        ttk.Label(control_frame, text="Number of tasks:").grid(row=0, column=0, padx=5)
        self.num_tasks_var = tk.StringVar(value="3")
        ttk.Entry(control_frame, textvariable=self.num_tasks_var, width=10).grid(row=0, column=1, padx=5)
        
        # Task type selection
        ttk.Label(control_frame, text="Task type:").grid(row=0, column=2, padx=5)
        self.task_type = tk.StringVar(value="random")
        task_combo = ttk.Combobox(control_frame, textvariable=self.task_type, width=15)
        task_combo['values'] = ('random', 'sequential', 'cpu_intensive')
        task_combo.grid(row=0, column=3, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=4, padx=5)
        
        ttk.Button(button_frame, text="Start Tasks", command=self.start_tasks).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Stop All", command=self.stop_all_tasks).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(main_container, text="Statistics", padding="5")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_vars = {
            'active': tk.StringVar(value="Active: 0"),
            'completed': tk.StringVar(value="Completed: 0"),
            'error': tk.StringVar(value="Errors: 0"),
            'total': tk.StringVar(value="Total: 0")
        }
        
        for i, (key, var) in enumerate(self.stats_vars.items()):
            ttk.Label(stats_frame, textvariable=var).grid(row=0, column=i, padx=20)
        
        # Thread status panel
        status_frame = ttk.LabelFrame(main_container, text="Thread Status", padding="5")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create and configure the treeview
        self.status_tree = ttk.Treeview(
            status_frame,
            columns=("ID", "State", "Progress", "Result"),
            show="headings",
            height=10
        )
        
        # Configure column widths and headings
        self.status_tree.heading("ID", text="Thread ID")
        self.status_tree.heading("State", text="State")
        self.status_tree.heading("Progress", text="Progress")
        self.status_tree.heading("Result", text="Result")
        
        self.status_tree.column("ID", width=80)
        self.status_tree.column("State", width=100)
        self.status_tree.column("Progress", width=150)
        self.status_tree.column("Result", width=200)
        
        self.status_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar to status tree
        status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        status_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_tree.configure(yscrollcommand=status_scroll.set)
        
        # Log panel
        log_frame = ttk.LabelFrame(main_container, text="Log", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(3, weight=1)
        status_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        # Tag configuration for treeview
        for state, (bg, fg) in ThreadState.COLORS.items():
            self.status_tree.tag_configure(state, background=bg, foreground=fg)
    
    def example_task(self, task_id):
        """Example task that simulates work"""
        self.log(f"Task {task_id} started")
        total_steps = 5
        
        try:
            for step in range(total_steps):
                if self.task_type.get() == 'random':
                    # Random workload between 0.5 and 1.5 seconds
                    work_time = random.uniform(0.5, 1.5)
                    time.sleep(work_time)
                    
                elif self.task_type.get() == 'sequential':
                    # Sequential workload with consistent 0.5 second steps
                    work_time = 0.5
                    time.sleep(work_time)
                    
                else:  # cpu_intensive
                    # CPU intensive workload with longer processing time
                    work_time = 2.0
                    # Simulate CPU-intensive work with a tight loop
                    end_time = time.time() + work_time
                    while time.time() < end_time:
                        # Perform some CPU-intensive calculations
                        _ = [i**2 for i in range(10000)]
                
                self.log(f"Task {task_id} completed step {step + 1}/{total_steps}")
                
                # Update progress in the queue
                progress = f"{(step + 1) * 100 // total_steps}%"
                self.update_queue.put(('progress', task_id, progress))
            
            result = f"Completed all {total_steps} steps"
            return result
            
        except Exception as e:
            self.log(f"Task {task_id} error: {str(e)}")
            raise
    
    def start_tasks(self):
        """Start the specified number of tasks"""
        try:
            num_tasks = int(self.num_tasks_var.get())
            if num_tasks <= 0:
                raise ValueError("Number of tasks must be positive")
            if num_tasks > 10:
                raise ValueError("Maximum 10 tasks allowed")
                
            self.log(f"Starting {num_tasks} tasks...")
            
            # Clear existing items in the tree
            for item in self.status_tree.get_children():
                self.status_tree.delete(item)
            
            # Reset statistics
            self.update_statistics()
            
            # Submit tasks
            for i in range(num_tasks):
                thread_id = self.thread_manager.submit_task(self.example_task, i)
                self.status_tree.insert("", tk.END, iid=str(thread_id),
                                      values=(thread_id, "IDLE", "0%", ""),
                                      tags=("IDLE",))
                
        except ValueError as e:
            self.log(f"Error: {str(e)}")
    
    def stop_all_tasks(self):
        """Stop all running tasks"""
        self.log("Stopping all tasks...")
        self.thread_manager.shutdown(wait=False)
        self.thread_manager = ThreadManager(max_workers=10)  # Create new manager
        self.log("All tasks stopped")
    
    def update_statistics(self):
        """Update the statistics display"""
        active = sum(1 for info in self.thread_manager._threads.values()
                    if info.state.name == 'RUNNING')
        completed = sum(1 for info in self.thread_manager._threads.values()
                       if info.state.name == 'TERMINATED')
        errors = sum(1 for info in self.thread_manager._threads.values()
                    if info.state.name == 'ERROR')
        total = len(self.thread_manager._threads)
        
        self.stats_vars['active'].set(f"Active: {active}")
        self.stats_vars['completed'].set(f"Completed: {completed}")
        self.stats_vars['error'].set(f"Errors: {errors}")
        self.stats_vars['total'].set(f"Total: {total}")
    
    def update_gui(self):
        """Update the GUI with thread status"""
        while True:
            try:
                time.sleep(0.1)  # Update every 100ms
                
                # Process any pending progress updates
                while not self.update_queue.empty():
                    update_type, *args = self.update_queue.get()
                    if update_type == 'progress':
                        task_id, progress = args
                        try:
                            item = self.status_tree.item(str(task_id))
                            values = list(item['values'])
                            values[2] = progress
                            self.status_tree.item(str(task_id), values=values)
                        except tk.TclError:
                            pass  # Item might have been removed
                    else:  # log message
                        message = args[0]
                        self.log_text.insert(tk.END, message + "\n")
                        self.log_text.see(tk.END)
                
                # Update thread status in tree
                for thread_id, thread_info in self.thread_manager._threads.items():
                    state = thread_info.state.name
                    result = thread_info.result if thread_info.result else ""
                    if thread_info.error:
                        result = f"Error: {str(thread_info.error)}"
                    
                    # Update treeview item
                    try:
                        item = self.status_tree.item(str(thread_id))
                        if item:
                            values = list(item['values'])
                            values[1] = state
                            values[3] = result
                            self.status_tree.item(str(thread_id), values=values, tags=(state,))
                    except tk.TclError:
                        pass  # Item might have been removed
                
                # Update statistics
                self.update_statistics()
            except Exception as e:
                self.log(f"GUI update error: {str(e)}")
                time.sleep(1)  # Wait a bit longer on error
    
    def log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.update_queue.put(('log', f"[{timestamp}] {message}"))
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = ThreadManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 