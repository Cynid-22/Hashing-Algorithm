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
import os
from typing import Optional

# Import from new modules
from config import HashAlgorithm
from components import StatusIndicator, ToolTip
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
        self.selected_file_paths: list[str] = []
        self._calculation_thread: Optional[threading.Thread] = None
        self._cancel_flag = False
        self._debounce_timer = None
        
        # Initialize logic engine
        self.hasher = HashCalculator()
        
        # Calculate thread count: 20% of CPU cores, minimum 1
        self._thread_count = max(1, int(multiprocessing.cpu_count() * 0.2))
        
        # Auto-calculate toggle variable
        self.auto_calc_var = tk.BooleanVar(value=False)
        
        self._setup_window()
        self._create_widgets()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Secure Hash Algorithm GUI")
        self.root.geometry("750x500")
        self.root.resizable(True, True)
        self.root.minsize(600, 400)
        
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
        
        # Create Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Hash Option Menu
        self.hash_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Hash Option", menu=self.hash_menu)
        
        # Algorithm variables
        self.algo_vars = {}
        algorithms = HashAlgorithm.all()
        
        for algo in algorithms:
            var = tk.BooleanVar(value=(algo == algorithms[0])) # Default first one selected
            self.hash_menu.add_checkbutton(label=algo, variable=var, command=self._on_input_change)
            self.algo_vars[algo] = var
            
        # Top row: Mode selection (Algorithm dropdown removed)
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=pad_x, pady=(20, pad_y))
        
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
            height=8,
            width=200,
            wrap=tk.WORD
        )
        self.input_text.bind('<Key>', self._on_input_change)
        
        # File mode widgets
        self.file_label = ttk.Label(self.input_container, text="Files:")
        
        self.file_frame = ttk.Frame(self.input_container)
        
        # Listbox with scrollbar
        self.file_list_frame = ttk.Frame(self.file_frame)
        self.file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.file_scrollbar = ttk.Scrollbar(self.file_list_frame)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            self.file_list_frame, 
            selectmode=tk.EXTENDED,
            yscrollcommand=self.file_scrollbar.set,
            height=8,
            activestyle='dotbox'
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scrollbar.config(command=self.file_listbox.yview)
        self.file_listbox.bind('<<ListboxSelect>>', self._on_file_select)
        
        # Buttons frame
        self.file_btn_frame = ttk.Frame(self.file_frame)
        self.file_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        
        self.add_file_btn = ttk.Button(self.file_btn_frame, text="+", width=3, command=self._add_files)
        self.add_file_btn.pack(side=tk.TOP, pady=(0, 5))
        ToolTip(self.add_file_btn, "Add file(s)")
        
        self.add_folder_btn = ttk.Button(self.file_btn_frame, text="+F", width=3, command=self._add_folder)
        self.add_folder_btn.pack(side=tk.TOP, pady=(0, 5))
        ToolTip(self.add_folder_btn, "Add folder (files only)")
        
        self.remove_file_btn = ttk.Button(self.file_btn_frame, text="-", width=3, command=self._remove_files, state="disabled")
        self.remove_file_btn.pack(side=tk.TOP)
        ToolTip(self.remove_file_btn, "Remove selected file(s)")
        
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
        
        self.auto_calc_check = ttk.Checkbutton(
            button_frame,
            text="Calculate Immediately",
            variable=self.auto_calc_var,
            command=self._on_auto_calc_toggle
        )
        
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
            height=6,
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
            self.calculate_button.pack(side=tk.LEFT, padx=(0, 10))
            self.auto_calc_check.pack(side=tk.LEFT, padx=(10, 0))
            self._on_auto_calc_toggle() # Update button state
        else:  # File mode
            # Show file input widgets
            self.file_label.pack(anchor=tk.W, pady=(0, 5))
            self.file_frame.pack(fill=tk.BOTH, expand=True)
            # Show calculate button in file mode
            self.calculate_button.pack(side=tk.LEFT, padx=(0, 10))
            self.auto_calc_check.pack_forget()
            self.calculate_button.config(state="normal") # Always enabled in file mode
        
        # Clear result and set input changed status
        self._set_result("")
        self.status_indicator.set_input_changed()
    
    def _on_input_change(self, event=None) -> None:
        """Handle input change event."""
        # Show input changed status
        self.status_indicator.set_input_changed()
        # Schedule hash calculation (only for text mode auto-calc)
        if self.mode_var.get() == "Text" and self.auto_calc_var.get():
            if self._debounce_timer:
                self.root.after_cancel(self._debounce_timer)
            self._debounce_timer = self.root.after(200, self._calculate_hash)
        
    def _on_auto_calc_toggle(self) -> None:
        """Handle auto-calculate checkbox toggle."""
        if self.mode_var.get() == "Text":
            if self.auto_calc_var.get():
                self.calculate_button.config(state="disabled")
                self._calculate_hash()
            else:
                self.calculate_button.config(state="normal")
        
    def _add_files(self) -> None:
        """Open file dialog and add selected files."""
        file_paths = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("All files", "*.*")]
        )
        
        if file_paths:
            for path in file_paths:
                if path not in self.selected_file_paths:
                    self.selected_file_paths.append(path)
                    self.file_listbox.insert(tk.END, os.path.basename(path))
            
            # Show input changed status
            self.status_indicator.set_input_changed()
            
    def _add_folder(self) -> None:
        """Open directory dialog and add all files in the folder."""
        folder_path = filedialog.askdirectory(title="Select folder")
        
        if folder_path:
            # Scan folder for files (non-recursive)
            try:
                for entry in os.scandir(folder_path):
                    if entry.is_file():
                        path = entry.path
                        if path not in self.selected_file_paths:
                            self.selected_file_paths.append(path)
                            self.file_listbox.insert(tk.END, entry.name)
                
                # Show input changed status
                self.status_indicator.set_input_changed()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read folder: {e}")
            
    def _remove_files(self) -> None:
        """Remove selected files from the list."""
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.file_listbox.delete(index)
            del self.selected_file_paths[index]
            
        self._on_file_select(None)
        self.status_indicator.set_input_changed()
        
    def _on_file_select(self, event=None) -> None:
        """Handle file selection change."""
        if self.file_listbox.curselection():
            self.remove_file_btn.config(state="normal")
        else:
            self.remove_file_btn.config(state="disabled")
                
    def _calculate_hash(self, event=None) -> None:
        """Calculate the hash using the selected algorithms."""
        selected_algos = [algo for algo, var in self.algo_vars.items() if var.get()]
        
        if not selected_algos:
            if self.mode_var.get() == "File" or event is None: # Only show warning if explicit click or file mode
                 messagebox.showwarning("Warning", "No hash algorithm selected!")
            return

        # For file mode, use threading; for text mode, run synchronously
        if self.mode_var.get() == "File":
            if not self.selected_file_paths:
                messagebox.showwarning("Warning", "No files selected!")
                return
                
            # File mode - use background thread
            if self._calculation_thread and self._calculation_thread.is_alive():
                return  # Already calculating
            
            self._cancel_flag = False
            self.status_indicator.set_calculating(0)
            self._set_result("") # Clear previous results
            
            # Define callbacks for the thread
            def progress_cb(p):
                # We'll update this to show overall progress or current file progress
                self.root.after(0, self.status_indicator.set_calculating, p)
                
            def check_cancel_cb():
                return self._cancel_flag
                
            def error_cb(msg):
                self.root.after(0, lambda: messagebox.showerror("Error", msg))
                
            def success_cb(res):
                # This is called per file, we need to append result
                pass 
            
            # Wrapper to process all files
            def process_files():
                total_files = len(self.selected_file_paths)
                
                for i, file_path in enumerate(self.selected_file_paths):
                    if self._cancel_flag:
                        break
                        
                    filename = os.path.basename(file_path)
                    prefix = f"{i+1}/{total_files} "
                    
                    # Update status initially
                    self.root.after(0, lambda p=prefix: self.status_indicator.set_calculating(None, p))
                    
                    # Local progress callback with prefix
                    def file_progress_cb(p):
                        self.root.after(0, lambda: self.status_indicator.set_calculating(p, prefix))
                    
                    # Local success callback to append result
                    def file_success_cb(results_dict):
                        result_str = f"{file_path}:\n"
                        for algo, hash_val in results_dict.items():
                            result_str += f"{algo}: {hash_val}\n"
                        result_str += "\n"
                        self.root.after(0, self._append_result, result_str)
                    
                    # Calculate hash for this file
                    self.hasher.calculate_file(
                        selected_algos, 
                        file_path, 
                        file_progress_cb, 
                        check_cancel_cb, 
                        error_cb, 
                        file_success_cb
                    )
                
                self.root.after(0, self.status_indicator.set_complete)

            # Start thread
            self._calculation_thread = threading.Thread(
                target=process_files,
                daemon=True
            )
            self._calculation_thread.start()
        else:
            # Text mode - run synchronously
            self.status_indicator.set_calculating()
            self.root.update_idletasks()
            
            try:
                text = self.input_text.get('1.0', tk.END).rstrip('\n')
                results = self.hasher.calculate_text_sync(selected_algos, text)
                
                result_str = ""
                for algo, hash_val in results.items():
                    result_str += f"{algo}: {hash_val}\n"
                
                self._set_result(result_str)
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
        
    def _append_result(self, text: str) -> None:
        """Append text to the result text box."""
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
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
            self.selected_file_paths = []
            self.file_listbox.delete(0, tk.END)
            self.remove_file_btn.config(state="disabled")
        
        self._set_result('')
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
