#!/usr/bin/env python3
"""
Secure Hash Algorithm GUI
A graphical interface for calculating SHA-256, SHA-384, and SHA-512 hashes.
No compilation required - uses Python's built-in hashlib library.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import hashlib
from typing import Optional


class HashAlgorithm:
    """Enum-like class for hash algorithm types."""
    SHA256 = "SHA-256"
    SHA384 = "SHA-384"
    SHA512 = "SHA-512"
    
    @classmethod
    def get_hash_function(cls, algorithm: str):
        """
        Get the hashlib function for the given algorithm.
        
        Args:
            algorithm: The algorithm name (e.g., "SHA-256")
            
        Returns:
            The corresponding hashlib function
        """
        mapping = {
            cls.SHA256: hashlib.sha256,
            cls.SHA384: hashlib.sha384,
            cls.SHA512: hashlib.sha512
        }
        return mapping.get(algorithm)
    
    @classmethod
    def all(cls) -> list:
        """Return all available algorithms."""
        return [cls.SHA256, cls.SHA384, cls.SHA512]


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
        self.root.geometry("550x450")
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
        
        # Algorithm selection
        algo_frame = ttk.Frame(self.root)
        algo_frame.pack(fill=tk.X, padx=pad_x, pady=(20, pad_y))
        
        ttk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        
        self.algorithm_var = tk.StringVar(value=HashAlgorithm.SHA256)
        self.algorithm_combo = ttk.Combobox(
            algo_frame,
            textvariable=self.algorithm_var,
            values=HashAlgorithm.all(),
            state="readonly",
            width=20
        )
        self.algorithm_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Input text section
        ttk.Label(self.root, text="Input Text:").pack(
            anchor=tk.W, padx=pad_x, pady=(pad_y, 5)
        )
        
        self.input_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            width=60,
            wrap=tk.WORD
        )
        self.input_text.pack(padx=pad_x, pady=(0, pad_y))
        
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
        ttk.Label(self.root, text="Hash Result:").pack(
            anchor=tk.W, padx=pad_x, pady=(pad_y, 5)
        )
        
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.X, padx=pad_x, pady=(0, pad_y))
        
        self.result_text = tk.Entry(
            result_frame,
            state="readonly",
            readonlybackground="white",
            font=("Courier", 9)
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            result_frame,
            text="Copy",
            command=self._copy_result,
            width=8
        ).pack(side=tk.LEFT, padx=(10, 0))
        
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
                
    def _calculate_hash(self) -> None:
        """Calculate the hash using the selected algorithm."""
        algorithm = self.algorithm_var.get()
        hash_func = HashAlgorithm.get_hash_function(algorithm)
        
        if not hash_func:
            messagebox.showerror("Error", f"Unknown algorithm: {algorithm}")
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
            
            # Calculate hash
            hash_obj = hash_func()
            hash_obj.update(input_bytes)
            hash_result = hash_obj.hexdigest()
            
            # Display the result
            self._set_result(hash_result)
            
        except Exception as ex:
            messagebox.showerror("Error", f"Error calculating hash: {ex}")
            
    def _set_result(self, text: str) -> None:
        """
        Set the result text box value.
        
        Args:
            text: The text to display
        """
        self.result_text.config(state="normal")
        self.result_text.delete(0, tk.END)
        self.result_text.insert(0, text)
        self.result_text.config(state="readonly")
        
    def _copy_result(self) -> None:
        """Copy the hash result to clipboard."""
        result = self.result_text.get()
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
