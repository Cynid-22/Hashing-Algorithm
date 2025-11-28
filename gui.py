#!/usr/bin/env python3
"""
Hash Algorithm GUI
A graphical interface for calculating SHA-256, SHA-384, SHA-512, and CRC-32 hashes.
Uses compiled C++ executables for hash calculations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import multiprocessing
from typing import Optional

# Import from new modules
from config import HashAlgorithm
from components import StatusIndicator
from hasher import HashCalculator


class SecureHashGUI:
    """Main GUI application for secure hash calculation."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the Secure Hash GUI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.selected_file_path: Optional[str] = None
        self._calculation_thread: Optional[threading.Thread] = None
        self._cancel_flag = False
        
        # Initialize logic engine
        self.hasher = HashCalculator()
        
        # Calculate thread count: 20% of CPU cores, minimum 1
        self._thread_count = max(1, int(multiprocessing.cpu_count() * 0.2))
        
        self._setup_window()
        self._create_widgets()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Secure Hash Algorithm GUI")
        self.root.geometry("750x450")
        self.root.resizable(False, False)
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self) -> None:
        """Create and layout all GUI widgets."""
        # Configure padding
        pad_x = 20
        pad_y = 10
        
        # Top row: Algorithm and Mode selection
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=pad_x, pady=(20, pad_y))
        
        # Algorithm selection
        ttk.Label(top_frame, text="Algorithm:").pack(side=tk.LEFT)
        
        algorithms = HashAlgorithm.all()
        default_algo = algorithms[0] if algorithms else ""
        
        self.algorithm_var = tk.StringVar(value=default_algo)
        self.algorithm_combo = ttk.Combobox(
            top_frame,
            textvariable=self.algorithm_var,
            values=HashAlgorithm.all(),
            state="readonly",
            width=15
        )
        self.algorithm_combo.pack(side=tk.LEFT, padx=(10, 20))
        self.algorithm_combo.bind('<<ComboboxSelected>>', self._on_input_change)
        
        # Mode selection
        ttk.Label(top_frame, text="Mode:").pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="Text")
        self.mode_combo = ttk.Combobox(
            top_frame,
            textvariable=self.mode_var,
            values=["Text", "File"],
            state="readonly",
            width=10
        )
        self.mode_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_change)
        
        # Input section container
        self.input_container = ttk.Frame(self.root)
        self.input_container.pack(fill=tk.BOTH, expand=True, padx=pad_x, pady=(0, pad_y))
        
        # Text mode widgets
        self.text_label = ttk.Label(self.input_container, text="Input:")
        self.input_text = scrolledtext.ScrolledText(
            self.input_container,
            height=6,
            width=200,
            wrap=tk.WORD
        )
        self.input_text.bind('<Key>', self._on_input_change)
        
        # File mode widgets
        self.file_label = ttk.Label(self.input_container, text="File:")
        self.file_frame = ttk.Frame(self.input_container)
        self.file_path_var = tk.StringVar(value="No file selected")
        self.file_path_label = ttk.Label(
            self.file_frame,
            textvariable=self.file_path_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.browse_button = ttk.Button(
            self.file_frame,
            text="Browse...",
            command=self._browse_file
        )
        
        # Action buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=pad_x, pady=pad_y)
        
        self.calculate_button = ttk.Button(
            button_frame,
            text="Calculate Hash",
            command=self._calculate_hash
        )
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_all
        ).pack(side=tk.LEFT)
        
        # Result section
        result_label_frame = ttk.Frame(self.root)
        result_label_frame.pack(fill=tk.X, padx=pad_x, pady=(pad_y, 5))
        
        ttk.Label(result_label_frame, text="Digest:").pack(side=tk.LEFT)
        
        self.status_indicator = StatusIndicator(result_label_frame)
        self.status_indicator.pack(side=tk.RIGHT)
        
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=pad_x, pady=(0, pad_y))
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=4,
            state="disabled",
            font=("Courier", 9)
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Button(
            result_frame,
            text="Copy",
            command=self._copy_result,
            width=8
        ).pack(side=tk.LEFT, padx=(10, 0), anchor=tk.N)
        
        # Initialize to text mode
        self._on_mode_change()
    
    def _on_mode_change(self, event=None) -> None:
        """Handle mode change between Text and File."""
        mode = self.mode_var.get()
        
        # Hide all input widgets first
        self.text_label.pack_forget()
        self.input_text.pack_forget()
        self.file_label.pack_forget()
        self.file_frame.pack_forget()
        self.calculate_button.pack_forget()
        
        if mode == "Text":
            # Show text input widgets
            self.text_label.pack(anchor=tk.W, pady=(0, 5))
            self.input_text.pack(fill=tk.BOTH, expand=True)
            self.selected_file_path = None
        else:  # File mode
            # Show file input widgets
            self.file_label.pack(anchor=tk.W, pady=(0, 5))
            self.file_frame.pack(fill=tk.X)
            self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self.browse_button.pack(side=tk.LEFT)
            # Show calculate button in file mode
            self.calculate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear result and set input changed status
        self._set_result("")
        self.status_indicator.set_input_changed()
    
    def _on_input_change(self, event=None) -> None:
        """Handle input change event."""
        # Show input changed status
        self.status_indicator.set_input_changed()
        # Schedule hash calculation
        self.root.after_idle(self._calculate_hash)
        
    def _browse_file(self) -> None:
        """Open file dialog and store file path for later hashing."""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            # Store file path without reading the file yet
            self.selected_file_path = file_path
            self.file_path_var.set(file_path)
            # Show input changed status
            self.status_indicator.set_input_changed()
                
    def _calculate_hash(self, event=None) -> None:
        """Calculate the hash using the selected algorithm."""
        algorithm = self.algorithm_var.get()
        
        # For file mode, use threading; for text mode, run synchronously
        if self.selected_file_path is not None:
            # File mode - use background thread
            if self._calculation_thread and self._calculation_thread.is_alive():
                return  # Already calculating
            
            self._cancel_flag = False
            self.status_indicator.set_calculating(0)
            
            # Define callbacks for the thread
            def progress_cb(p):
                self.root.after(0, self.status_indicator.set_calculating, p)
                
            def check_cancel_cb():
                return self._cancel_flag
                
            def error_cb(msg):
                self.root.after(0, lambda: messagebox.showerror("Error", msg))
                self.root.after(0, self.status_indicator.set_complete)
                
            def success_cb(res):
                self.root.after(0, self._set_result, res)
                self.root.after(0, self.status_indicator.set_complete)
            
            # Start thread
            self._calculation_thread = threading.Thread(
                target=self.hasher.calculate_file,
                args=(algorithm, self.selected_file_path, progress_cb, check_cancel_cb, error_cb, success_cb),
                daemon=True
            )
            self._calculation_thread.start()
        else:
            # Text mode - run synchronously
            self.status_indicator.set_calculating()
            self.root.update_idletasks()
            
            try:
                text = self.input_text.get('1.0', tk.END).rstrip('\n')
                result = self.hasher.calculate_text_sync(algorithm, text)
                self._set_result(result)
            except Exception as ex:
                messagebox.showerror("Error", str(ex))
            finally:
                self.status_indicator.set_complete()
    
    def _on_closing(self) -> None:
        """Handle window closing with proper cleanup."""
        # Set cancel flag
        self._cancel_flag = True
        
        # Terminate any subprocesses in the hasher
        self.hasher.terminate_subprocess()
        
        # Wait for calculation thread
        if self._calculation_thread and self._calculation_thread.is_alive():
            self._calculation_thread.join(timeout=2.0)
        
        # Destroy window
        self.root.destroy()
            
    def _set_result(self, text: str) -> None:
        """Set the result text box value."""
        self.result_text.config(state="normal")
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', text)
        self.result_text.config(state="disabled")
        
    def _copy_result(self) -> None:
        """Copy the hash result to clipboard."""
        result = self.result_text.get('1.0', 'end-1c')
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            messagebox.showinfo("Success", "Hash copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No hash result to copy!")
            
    def _clear_all(self) -> None:
        """Clear both input and result text boxes."""
        mode = self.mode_var.get()
        
        if mode == "Text":
            self.input_text.delete('1.0', tk.END)
        else:  # File mode
            self.file_path_var.set("No file selected")
        
        self._set_result('')
        self.selected_file_path = None
        self.status_indicator.set_input_changed()
            
    def run(self) -> None:
        """Start the GUI event loop."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = SecureHashGUI(root)
    app.run()


if __name__ == "__main__":
    main()
