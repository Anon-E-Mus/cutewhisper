"""
Audio Visualizer - Thin rounded bars in rectangular window
"""

import tkinter as tk
import time
import threading
import logging
import numpy as np
import math

logger = logging.getLogger(__name__)


class AudioVisualizerWindow:
    """Recording indicator with thin rounded bars"""

    def __init__(self):
        self.window = None
        self.canvas = None
        self.bars = []
        self.running = False
        self.update_timer = None
        self.root = None
        self.lock = threading.Lock()
        self.current_audio_level = 0.0

        # Rectangular window dimensions
        self.width = 160
        self.height = 40

        # Bar configuration - more bars, thinner
        self.num_bars = 16  # Number of bars
        self.bar_width = 4   # Thinner bars
        self.bar_spacing = 4

    def show(self):
        """Thread-safe show"""
        with self.lock:
            if self.window:
                return

        if self.root:
            self.root.after(0, self._show_in_main_thread)
        else:
            self._show_in_main_thread()

    def _show_in_main_thread(self):
        """Actually show the window"""
        with self.lock:
            if self.window:
                return

            if not self.root:
                self.root = tk.Tk()
                self.root.withdraw()

            # Create window
            self.window = tk.Toplevel(self.root)
            self.window.title("Recording")

            # Remove decorations
            self.window.overrideredirect(True)

            # Make always on top
            self.window.attributes('-topmost', True)

            # Semi-transparent
            self.window.attributes('-alpha', 0.95)

            # Center at top of screen
            screen_width = self.window.winfo_screenwidth()
            x = (screen_width - self.width) // 2
            self.window.geometry(f"{self.width}x{self.height}+{x}+20")

            # Create canvas
            self.canvas = tk.Canvas(
                self.window,
                width=self.width,
                height=self.height,
                bg='black',  # Black background
                highlightthickness=0,
                relief='flat',
                bd=0
            )
            self.canvas.pack()

            # Create audio bars with rounded tops
            self._create_bars()

            # Start
            self.running = True
            self.current_audio_level = 0.0

            self._animate()

    def _create_bars(self):
        """Create audio bars on canvas - CAPSULE SHAPE (rectangle + rounded ends)"""
        # Calculate total width and center it
        total_width = (self.num_bars * self.bar_width) + ((self.num_bars - 1) * self.bar_spacing)
        start_x = (self.width - total_width) // 2
        y_center = self.height // 2

        for i in range(self.num_bars):
            x = start_x + (i * (self.bar_width + self.bar_spacing))

            # Create capsule-shaped bar: rectangle + two circular ends
            # Each bar has 3 parts: top circle (end), middle rectangle, bottom circle (end)
            bar_parts = []

            # Initial height (will be animated) - start invisible (black)
            initial_height = 4
            half_height = initial_height // 2

            # Width and radius (circle slightly smaller than rectangle)
            w = self.bar_width
            circle_diameter = w - 1  # Slightly smaller
            r = circle_diameter // 2

            # Rectangle edges
            rect_top = y_center - half_height
            rect_bottom = y_center + half_height

            # Center the circle horizontally on the rectangle
            circle_x_offset = (w - circle_diameter) // 2

            # Top circle - centered on top edge, smaller than rectangle width
            top_circle = self.canvas.create_oval(
                x + circle_x_offset, rect_top - r,
                x + circle_x_offset + circle_diameter, rect_top + r,
                fill='black',
                outline=''
            )
            bar_parts.append(top_circle)

            # Middle rectangle
            middle_rect = self.canvas.create_rectangle(
                x, rect_top,
                x + w, rect_bottom,
                fill='black',
                outline=''
            )
            bar_parts.append(middle_rect)

            # Bottom circle - centered on bottom edge, smaller than rectangle width
            bottom_circle = self.canvas.create_oval(
                x + circle_x_offset, rect_bottom - r,
                x + circle_x_offset + circle_diameter, rect_bottom + r,
                fill='black',
                outline=''
            )
            bar_parts.append(bottom_circle)

            self.bars.append({
                'parts': bar_parts,
                'x': x,
                'y_center': y_center,
                'index': i,
                'top_circle': top_circle,
                'middle_rect': middle_rect,
                'bottom_circle': bottom_circle
            })

    def update_audio_level(self, audio_data):
        """Update audio level from recorder callback"""
        try:
            if len(audio_data) > 0:
                audio_float = audio_data.astype(np.float32)
                rms = np.sqrt(np.mean(audio_float ** 2))
                level = min(rms * 20, 1.0)
                self.current_audio_level = (self.current_audio_level * 0.75) + (level * 0.25)
        except Exception as e:
            logger.debug(f"Audio level calculation error: {e}")

    def _animate(self):
        """Animation loop - symmetrical wave pattern with capsule-shaped bars"""
        if not self.running or not self.window:
            return

        try:
            # Create symmetrical wave pattern
            for i, bar in enumerate(self.bars):
                # Symmetrical position from center
                center_index = (self.num_bars - 1) / 2
                distance_from_center = abs(i - center_index)

                # Create wave pattern that peaks at center
                position_factor = 1.0 - (distance_from_center / center_index)

                # Add wave animation that moves outward from center
                wave = math.sin(time.time() * 4 + distance_from_center * 0.5) * 0.15

                # Combine position factor with audio level
                height_factor = (self.current_audio_level * position_factor) + wave

                # Clamp to valid range
                height_factor = max(0.0, min(height_factor, 1.0))

                # Calculate bar height
                max_bar_height = (self.height // 2) - 4
                bar_height = int(4 + (height_factor * max_bar_height))
                half_height = bar_height // 2

                # Determine visibility based on audio level
                # If height_factor is very low (< 0.05), make bar invisible (black)
                if height_factor < 0.05:
                    color = 'black'  # Invisible
                else:
                    # White for visible bars, with slight brightness variation
                    color = 'white'

                # Calculate coordinates
                x = int(bar['x'])
                yc = int(bar['y_center'])

                # Width and circle diameter (circle slightly smaller)
                w = self.bar_width
                circle_diameter = w - 1
                r = circle_diameter // 2
                circle_x_offset = (w - circle_diameter) // 2

                # Rectangle coordinates
                rect_top = yc - half_height
                rect_bottom = yc + half_height

                # Top circle - centered horizontally on rectangle, smaller width
                self.canvas.coords(
                    bar['top_circle'],
                    x + circle_x_offset, rect_top - r,
                    x + circle_x_offset + circle_diameter, rect_top + r
                )

                # Middle rectangle
                self.canvas.coords(bar['middle_rect'], x, rect_top, x + w, rect_bottom)

                # Bottom circle - centered horizontally on rectangle, smaller width
                self.canvas.coords(
                    bar['bottom_circle'],
                    x + circle_x_offset, rect_bottom - r,
                    x + circle_x_offset + circle_diameter, rect_bottom + r
                )

                # Update all parts with new color
                self.canvas.itemconfig(bar['top_circle'], fill=color)
                self.canvas.itemconfig(bar['middle_rect'], fill=color)
                self.canvas.itemconfig(bar['bottom_circle'], fill=color)

        except Exception as e:
            logger.error(f"Animation error: {e}")

        self.update_timer = self.window.after(33, self._animate)

    def hide(self):
        """Thread-safe hide"""
        if self.root:
            self.root.after(0, self._hide_in_main_thread)
        else:
            self._hide_in_main_thread()

    def _hide_in_main_thread(self):
        """Actually hide the window"""
        with self.lock:
            self.running = False
            if self.update_timer and self.window:
                self.window.after_cancel(self.update_timer)
                self.update_timer = None
            if self.window:
                self.window.destroy()
                self.window = None
                self.canvas = None
                self.bars = []
