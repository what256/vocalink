import tkinter as tk
import math
import time

class RecordingOverlay(tk.Toplevel):
    """A sleek, always-on-top, pill-shaped overlay with a live waveform animation."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recording_active = False
        self.alpha = 0.0  # Initial transparency
        self.fade_speed = 0.05  # How fast it fades in/out
        self.animation_speed = 50  # Milliseconds per animation frame

        # Configure window properties
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Always on top
        self.attributes('-alpha', self.alpha)  # Set initial transparency
        self.wm_attributes("-transparentcolor", "#000001")  # Set a transparent color key
        self.attributes('-toolwindow', True) # Prevent from appearing in taskbar (Windows)

        self.width = 150  # Smaller width
        self.height = 30  # Smaller height
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="#000001", highlightthickness=0)
        self.canvas.pack()

        self.geometry(f"{self.width}x{self.height}")
        self.update_idletasks()
        self._position_window()

        # Initial drawing of the pill shape (with shadow)
        # Shadow: slightly larger, offset, darker oval
        self.shadow_id = self.canvas.create_oval(2, 2, self.width + 2, self.height + 2, fill="#444444", outline="") # Softer, slightly lighter shadow
        self.pill_id = self.canvas.create_oval(0, 0, self.width, self.height, fill="#333333", outline="")
        self.waveform_id = None

    def _position_window(self):
        """Positions the window at the bottom-center, just above the taskbar."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        bottom_offset = 20  # Pixels above the taskbar (increased for more clearance)
        taskbar_height_estimate = 40 # Estimate for Windows taskbar height

        x = (screen_width - self.width) // 2 # Center horizontally
        y = screen_height - taskbar_height_estimate - self.height - bottom_offset

        self.geometry(f"+{x}+{y}")

    def show_overlay(self):
        """Starts showing the overlay and waveform animation."""
        if not self.recording_active:
            self.recording_active = True
            self.deiconify()  # Make the window visible
            self._fade_in()
            self._animate_waveform()

    def hide_overlay(self):
        """Starts fading out the overlay."""
        if self.recording_active:
            self.recording_active = False
            self._fade_out()

    def _fade_in(self):
        """Gradually increases the overlay's transparency."""
        if self.alpha < 1.0:
            self.alpha += self.fade_speed
            if self.alpha > 1.0: self.alpha = 1.0
            self.attributes('-alpha', self.alpha)
            self.after(20, self._fade_in)  # Call again after 20ms

    def _fade_out(self):
        """Gradually decreases the overlay's transparency."""
        if self.alpha > 0.0:
            self.alpha -= self.fade_speed
            if self.alpha < 0.0: self.alpha = 0.0
            self.attributes('-alpha', self.alpha)
            self.after(20, self._fade_out)
        else:
            # Ensure waveform is cleared when fully faded out
            if self.waveform_id: self.canvas.delete(self.waveform_id)
            self.waveform_id = None
            self.withdraw() # Hide the window completely when faded out

    def _animate_waveform(self):
        """Draws a simulated live red waveform animation."""
        if not self.recording_active and self.alpha <= 0.0:  # Stop animation if not active and faded
            if self.waveform_id: self.canvas.delete(self.waveform_id)
            self.waveform_id = None
            return

        self.canvas.delete("waveform")  # Clear previous waveforms using a tag

        points = []
        center_y = self.height / 2
        amplitude = self.height / 3
        num_points = 50
        x_step = self.width / num_points
        current_time = time.time() * 5 # Base time for animation

        # Draw multiple lines for a fuller waveform
        for line_offset in [-0.5, 0, 0.5]: # Draw 3 slightly offset lines
            points = []
            amplitude_factor = 1.0 - abs(line_offset) * 0.4 # Reduce amplitude for outer lines
            amplitude = (self.height / 3) * amplitude_factor

            for i in range(num_points):
                x = i * x_step
                # More complex sine wave with multiple frequencies for a richer look
                y = center_y                     + amplitude * math.sin(i * 0.3 + current_time + line_offset * 2)                     + (amplitude / 2) * math.sin(i * 0.8 + current_time * 1.5 + line_offset * 3)
                points.append((x, y))

            # Draw the waveform as a line with a tag
            if points:
                self.canvas.create_line(points, fill="#FF4444", width=2, smooth=True, tags="waveform")

        self.after(self.animation_speed, self._animate_waveform)

    def destroy(self):
        """Clean up on destroy."""
        self.recording_active = False
        super().destroy()
