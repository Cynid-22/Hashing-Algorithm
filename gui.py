#!/usr/bin/env python3
"""
Hash Algorithm GUI
A graphical interface for calculating SHA-256, SHA-384, SHA-512, and CRC-32 hashes.
Uses compiled C++ executables for hash calculations.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
from typing import Optional, Dict, List


class HashAlgorithm:
    """Dynamically loads hash algorithms from config file."""
    
    _algorithms: List[Dict] = []
    _config_loaded = False
    
    @classmethod
    def load_config(cls, config_path: str = "algorithms.json") -> None:
        """
        Load algorithms from the configuration file.
        
        Args:
            config_path: Path to the algorithms configuration file
        """
        if cls._config_loaded:
            return
            
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, config_path)
        
        try:
            with open(full_path, 'r') as f:
                config = json.load(f)
                cls._algorithms = config.get('algorithms', [])
                cls._config_loaded = True
        except FileNotFoundError:
            messagebox.showerror(
                "Configuration Error",
                f"Could not find {config_path}. Using default algorithms."
            )
            # Fallback to default algorithms
            cls._algorithms = [
                {"name": "SHA-256", "type": "hashlib", "hashlib_name": "sha256"},
                {"name": "SHA-384", "type": "hashlib", "hashlib_name": "sha384"},
                {"name": "SHA-512", "type": "hashlib", "hashlib_name": "sha512"}
            ]
            cls._config_loaded = True
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Configuration Error",
                f"Invalid JSON in {config_path}: {e}"
            )
            cls._algorithms = []
            cls._config_loaded = True
    
    @classmethod
    def get_algorithm_config(cls, name: str) -> Optional[Dict]:
        """
        Get the configuration for a specific algorithm.
        
        Args:
            name: The algorithm name
            
        Returns:
            The algorithm configuration dictionary or None
        """
        cls.load_config()
        for algo in cls._algorithms:
            if algo['name'] == name:
                return algo
        return None
    
    @classmethod
    def all(cls) -> List[str]:
        """Return all available algorithm names."""
        cls.load_config()
        return [algo['name'] for algo in cls._algorithms]


class StatusIndicator(tk.Frame):
    """Custom widget to display status with an icon and text."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Icon canvas
        self.canvas = tk.Canvas(self, width=20, height=20, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status text
        self.label = ttk.Label(self, text="")
        self.label.pack(side=tk.LEFT)
        
        self._angle = 0
        self._animating = False
        self._animation_id = None
        
        # Initial state
        self.set_complete()
        
    def set_calculating(self):
        """Set status to calculating with a spinner."""
        self._animating = True
        self.label.config(text="Calculating...")
        self._animate_spinner()
        
    def set_complete(self):
        """Set status to complete with a green check mark."""
        self._stop_animation()
        self.label.config(text="Complete")
        self._draw_check_mark()
    
    def set_input_changed(self):
        """Set status to input changed with a red X."""
        self._stop_animation()
        self.label.config(text="Input changed")
        self._draw_x_mark()
        
    def _draw_check_mark(self):
        """Draw a green check mark."""
        self.canvas.delete("all")
        # Draw circle
        self.canvas.create_oval(2, 2, 18, 18, outline="green", width=2)
        # Draw check
        self.canvas.create_line(5, 10, 9, 14, 15, 6, fill="green", width=2)
    
    def _draw_x_mark(self):
        """Draw a red X mark."""
        self.canvas.delete("all")
        # Draw circle
        self.canvas.create_oval(2, 2, 18, 18, outline="red", width=2)
        # Draw X
        self.canvas.create_line(6, 6, 14, 14, fill="red", width=2)
        self.canvas.create_line(14, 6, 6, 14, fill="red", width=2)
        
    def _animate_spinner(self):
        """Animate a rotating spinner."""
        if not self._animating:
            return
            
        self.canvas.delete("all")
        
        # Draw spinner arc
        start = self._angle
        extent = 270
        self.canvas.create_arc(2, 2, 18, 18, start=start, extent=extent, outline="blue", width=2, style="arc")
        
        self._angle = (self._angle + 20) % 360
        self._animation_id = self.after(50, self._animate_spinner)
        
    def _stop_animation(self):
        """Stop the spinner animation."""
        self._animating = False
        if self._animation_id:
            self.after_cancel(self._animation_id)
            self._animation_id = None


class SecureHashGUI:
    """Main GUI application for secure hash calculation."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the Secure Hash GUI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.binary_content: Optional[bytes] = None
        self._setup_window()
        self._create_widgets()
        

        
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
            self.binary_content = None
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
        """Open file dialog and load file for hashing."""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Always read as binary for consistent hashing
                with open(file_path, 'rb') as file:
                    self.binary_content = file.read()
                    # Update file path display
                    self.file_path_var.set(file_path)
                    # Show input changed status
                    self.status_indicator.set_input_changed()
            except Exception as ex:
                messagebox.showerror("Error", f"Error reading file: {ex}")
                
    def _calculate_hash(self, event=None) -> None:
        """Calculate the hash using the selected algorithm."""
        # Update status to calculating
        self.status_indicator.set_calculating()
        self.root.update_idletasks()
        
        algorithm = self.algorithm_var.get()
        algo_config = HashAlgorithm.get_algorithm_config(algorithm)
        
        if not algo_config:
            messagebox.showerror("Error", f"Unknown algorithm: {algorithm}")
            self.status_indicator.set_complete()
            return
            
        try:
            # Get input data
            if self.binary_content is not None:
                # Use stored binary content
                input_bytes = self.binary_content
            else:
                # Get text from input box and encode
                input_data = self.input_text.get('1.0', tk.END).rstrip('\n')
                input_bytes = input_data.encode('utf-8')
            
            # Calculate hash using C++ executable
            algo_type = algo_config.get('type')
            
            if algo_type == 'executable':
                # Get executable name
                executable_name = algo_config.get('executable')
                if not executable_name:
                    messagebox.showerror("Error", f"No executable specified for {algorithm}")
                    self.status_indicator.set_complete()
                    return
                
                # Get the directory where this script is located
                script_dir = os.path.dirname(os.path.abspath(__file__))
                executable_path = os.path.join(script_dir, executable_name)
                
                # Check if executable exists
                if not os.path.exists(executable_path):
                    messagebox.showerror(
                        "Error", 
                        f"Executable not found: {executable_name}\\n\\n"
                        f"Please compile the C++ files first.\\n"
                        f"Example: g++ -o {executable_name} {executable_name.replace('.exe', '.cpp')}"
                    )
                    self.status_indicator.set_complete()
                    return
                
                # Run the executable with input data via stdin
                try:
                    result = subprocess.run(
                        [executable_path],
                        input=input_bytes,
                        capture_output=True,
                        check=True,
                        timeout=5
                    )
                    # Get hash from stdout and strip whitespace
                    hash_result = result.stdout.decode('utf-8').strip()
                except subprocess.TimeoutExpired:
                    messagebox.showerror("Error", f"Hash calculation timed out")
                    self.status_indicator.set_complete()
                    return
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Hash calculation failed: {e}")
                    self.status_indicator.set_complete()
                    return
            else:
                messagebox.showerror("Error", f"Unknown algorithm type: {algo_type}")
                self.status_indicator.set_complete()
                return
            
            # Display the result
            self._set_result(hash_result)
            
        except Exception as ex:
            messagebox.showerror("Error", f"Error calculating hash: {ex}")
        finally:
            # Update status to complete
            self.status_indicator.set_complete()
            
    def _set_result(self, text: str) -> None:
        """
        Set the result text box value.
        
        Args:
            text: The text to display
        """
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
        self.binary_content = None
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
