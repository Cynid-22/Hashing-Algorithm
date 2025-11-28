"""
UI components for Hash Algorithm GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

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
        
    def set_calculating(self, progress: Optional[int] = None):
        """Set status to calculating with a spinner and optional progress."""
        self._animating = True
        if progress is not None:
            self.label.config(text=f"Calculating... {progress}%")
        else:
            self.label.config(text="Calculating...")
        if not self._animation_id:
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
