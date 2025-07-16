import customtkinter as ctk
import math
import time

class RecordingOverlay(ctk.CTkToplevel):
    """A sleek, always-on-top, pill-shaped overlay with a live waveform animation."""

    def __init__(self, parent):
        super().__init__(parent) # Inherit from CTkToplevel
        self.parent = parent
        self.recording_active = False
        self.alpha = 0.0  # Initial transparency
        self.fade_speed = 0.05  # How fast it fades in/out
        self.animation_speed = 50  # Milliseconds per animation frame

        # Configure window properties directly on self (the CTkToplevel)
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Always on top
        self.attributes('-alpha', self.alpha)  # Set initial transparency
        self.wm_attributes("-transparentcolor", "#000001")  # Set a transparent color key
        self.attributes('-toolwindow', True) # Prevent from appearing in taskbar (Windows)

        self.width = 180  # Slightly wider
        self.height = 35  # Slightly taller

        # Create a CTkCanvas as a child of this Toplevel window
        self.canvas = ctk.CTkCanvas(self, width=self.width, height=self.height, highlightthickness=0, bg="#000001") # Use transparent color key
        self.canvas.pack(fill="both", expand=True)

        self.update_idletasks()
        self._position_window()

        # Add rounded rectangle drawing method to canvas
        self.canvas.create_rounded_rectangle = self._create_rounded_rectangle_on_canvas

        # Initial drawing of the pill shape (with shadow)
        self.shadow_id = self.canvas.create_rounded_rectangle(5, 5, self.width + 5, self.height + 5, radius=25, fill="#000000", outline="") # Deeper shadow
        self.pill_id = self.canvas.create_rounded_rectangle(0, 0, self.width, self.height, radius=25, fill="#2C2C2C", outline="") # Refined pill color
        self.waveform_id = None

    def _create_rounded_rectangle_on_canvas(self, x1, y1, x2, y2, radius, **kwargs):
        """Helper to draw a rounded rectangle on the canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1 + radius, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _position_window(self):
        """Positions the window at the bottom-center, just above the taskbar."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        bottom_offset = -160  # Adjusted for better positioning
        taskbar_height_estimate = 0 # Estimate for Windows taskbar height.

        x = (screen_width - self.width) // 2 + 200 # Center horizontally and shift to the right
        y = screen_height - self.height - bottom_offset - taskbar_height_estimate
        self.geometry(f"+{x}+{y}")

        print(f"Screen: {screen_width}x{screen_height}, Overlay: {self.width}x{self.height}", flush=True)
        print(f"Calculated position: x={x}, y={y}", flush=True)
        print(f"Bottom offset: {bottom_offset}, Taskbar estimate: {taskbar_height_estimate}", flush=True)

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
            self.after(100, self.withdraw) # Add a small delay before withdrawing

    def _animate_waveform(self):
        """Draws a simulated live red waveform animation."""
        if not self.recording_active and self.alpha <= 0.0:  # Stop animation if not active and faded
            if self.waveform_id: self.canvas.delete(self.waveform_id)
            self.waveform_id = None
            return

        self.canvas.delete("waveform")  # Clear previous waveforms using a tag

        points = []
        center_y = self.height / 2
        amplitude_base = self.height / 2.5 # Adjusted for new height
        num_points = 60 # More points for smoother waveform
        x_step = self.width / num_points
        current_time = time.time() * 7 # Faster animation for more dynamism

        # Draw multiple lines for a fuller, more organic waveform
        for line_offset in [-0.8, -0.4, 0, 0.4, 0.8]: # Draw 5 slightly offset lines for more depth
            points = []
            amplitude_factor = 1.0 - abs(line_offset) * 0.2 # Reduce amplitude for outer lines
            amplitude = amplitude_base * amplitude_factor

            for i in range(num_points):
                x = i * x_step
                # More complex sine wave with multiple frequencies and a slight random component
                y = center_y                     + amplitude * math.sin(i * 0.25 + current_time + line_offset * 2.5)                     + (amplitude / 2.5) * math.sin(i * 0.75 + current_time * 1.8 + line_offset * 3.5)                     + (amplitude / 5) * math.sin(i * 1.5 + current_time * 3.0 + line_offset * 5)
                points.append((x, y))

            # Draw the waveform as a line with a tag
            if points:
                self.canvas.create_line(points, fill="#00FF00", width=2, smooth=True, tags="waveform") # Bright green waveform # Bright green waveform

        self.after(self.animation_speed, self._animate_waveform)

    def destroy(self):
        """Clean up on destroy."""
        self.recording_active = False
        super().destroy()