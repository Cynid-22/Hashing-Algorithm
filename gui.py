#!/usr/bin/env python3
"""
Hash Algorithm GUI
A graphical interface for calculating SHA-256, SHA-384, SHA-512, and CRC-32 hashes.
No compilation required - uses Python's built-in hashlib library and custom CRC implementation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import hashlib
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
    def get_hash_function(cls, algorithm: str):
        """
        Get the hashlib function for the given algorithm.
        
        Args:
            algorithm: The algorithm name
            
        Returns:
            The corresponding hashlib function or None for custom algorithms
        """
        cls.load_config()
        config = cls.get_algorithm_config(algorithm)
        
        if config and config.get('type') == 'hashlib':
            hashlib_name = config.get('hashlib_name')
            return getattr(hashlib, hashlib_name, None)
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
        
    def _draw_check_mark(self):
        """Draw a green check mark."""
        self.canvas.delete("all")
        # Draw circle
        self.canvas.create_oval(2, 2, 18, 18, outline="green", width=2)
        # Draw check
        self.canvas.create_line(5, 10, 9, 14, 15, 6, fill="green", width=2)
        
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
    
    # CRC-32 lookup table (generated once at class level)
    CRC32_TABLE = None
    
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
        self._generate_crc32_table()
        
    @classmethod
    def _generate_crc32_table(cls) -> None:
        """Generate CRC-32 lookup table (IEEE 802.3 polynomial)."""
        if cls.CRC32_TABLE is not None:
            return
            
        cls.CRC32_TABLE = []
        CRC32_POLYNOMIAL = 0xEDB88320
        
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ CRC32_POLYNOMIAL
                else:
                    crc >>= 1
            cls.CRC32_TABLE.append(crc)
    
    def _calculate_crc32(self, data: bytes) -> str:
        """
        Calculate CRC-32 checksum.
        
        Args:
            data: The input bytes
            
        Returns:
            The CRC-32 checksum as hexadecimal string
        """
        crc = 0xFFFFFFFF
        
        for byte in data:
            index = (crc ^ byte) & 0xFF
            crc = (crc >> 8) ^ self.CRC32_TABLE[index]
        
        crc ^= 0xFFFFFFFF
        return f"{crc:08x}"
        
    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Secure Hash Algorithm GUI")
        self.root.geometry("750x450")
        self.root.resizable(False, False)
        
        # Remove window icon (delayed to prevent tkinter from overriding)
        self.root.after(200, self._remove_icon)
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    
    def _remove_icon(self) -> None:
        """Remove the window icon by setting it to a transparent image."""
        try:
            # Create a transparent 1x1 pixel image
            # This effectively makes the icon invisible
            blank_icon = tk.PhotoImage(width=1, height=1)
            blank_icon.blank()
            self.root.iconphoto(True, blank_icon)
        except Exception:
            # If that fails, try the empty bitmap approach
            try:
                self.root.iconbitmap('')
            except:
                pass
        
    def _create_widgets(self) -> None:
        """Create and layout all GUI widgets."""
        # Configure padding
        pad_x = 20
        pad_y = 10
        
        # Algorithm selection
        algo_frame = ttk.Frame(self.root)
        algo_frame.pack(fill=tk.X, padx=pad_x, pady=(20, pad_y))
        
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        
        # Get default algorithm (first in the list, or empty string if none)
        algorithms = HashAlgorithm.all()
        default_algo = algorithms[0] if algorithms else ""
        
        self.algorithm_var = tk.StringVar(value=default_algo)
        self.algorithm_combo = ttk.Combobox(
            algo_frame,
            textvariable=self.algorithm_var,
            values=HashAlgorithm.all(),
            state="readonly",
            width=20
        )
        self.algorithm_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.algorithm_combo.bind('<<ComboboxSelected>>', self._calculate_hash)
        
        # Input text section
        ttk.Label(self.root, text="Input:").pack(
            anchor=tk.W, padx=pad_x, pady=(pad_y, 5)
        )
        
        self.input_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            width=200,
            wrap=tk.WORD
        )
        self.input_text.pack(padx=pad_x, pady=(0, pad_y))
        self.input_text.bind('<Key>', lambda e: self.root.after_idle(self._calculate_hash))
        
        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=pad_x, pady=pad_y)
        
        ttk.Button(
            button_frame,
            text="Browse File...",
            command=self._browse_file
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Calculate Hash",
            command=self._calculate_hash
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_all
        ).pack(side=tk.LEFT, padx=(10, 0))
        
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
        
    def _browse_file(self) -> None:
        """Open file dialog and load file contents into input text box."""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Try to read as text first
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.delete('1.0', tk.END)
                    self.input_text.insert('1.0', content)
                    self.binary_content = None
            except UnicodeDecodeError:
                # If file is binary, read as bytes and display info
                try:
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        self.input_text.delete('1.0', tk.END)
                        self.input_text.insert(
                            '1.0',
                            f"[Binary file: {len(content)} bytes]\n"
                            f"Note: Hash will be calculated on raw bytes."
                        )
                        # Store the binary content for hashing
                        self.binary_content = content
                except Exception as ex:
                    messagebox.showerror("Error", f"Error reading file: {ex}")
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
            
            # Calculate hash based on algorithm type
            algo_type = algo_config.get('type')
            
            if algo_type == 'hashlib':
                # Use hashlib for standard algorithms
                hash_func = HashAlgorithm.get_hash_function(algorithm)
                if not hash_func:
                    messagebox.showerror("Error", f"Failed to load algorithm: {algorithm}")
                    self.status_indicator.set_complete()
                    return
                hash_obj = hash_func()
                hash_obj.update(input_bytes)
                hash_result = hash_obj.hexdigest()
                
            elif algo_type == 'custom':
                # Use custom implementation
                method_name = algo_config.get('method')
                if method_name == 'crc32':
                    hash_result = self._calculate_crc32(input_bytes)
                else:
                    messagebox.showerror("Error", f"Unknown custom method: {method_name}")
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
        self.input_text.delete('1.0', tk.END)
        self._set_result('')
        self.binary_content = None
            
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
