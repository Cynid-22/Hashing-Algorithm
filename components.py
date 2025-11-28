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
        self.label = ttk.Label(self, text="", width=35, anchor="w")
        self.label.pack(side=tk.LEFT)
        
        self._angle = 0
        self._animating = False
        self._animation_id = None
        
        # Initial state
        self.set_complete()
        
    def set_calculating(self, progress: Optional[int] = None, prefix: str = ""):
        """Set status to calculating with a spinner and optional progress."""
        self._animating = True
        if progress is not None:
            self.label.config(text=f"{prefix}Calculating... {progress}%")
        else:
            self.label.config(text=f"{prefix}Calculating...")
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


class ToolTip:
    """
    Creates a tooltip for a given widget as the mouse hovers on it.
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # miliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
