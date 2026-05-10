import time
import math
import random
from PIL import Image, ImageDraw
from .base import Widget

class GeometryWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        
        self.scenes = ["moire", "kaleidoscope", "tunnel", "spirograph"]
        self.scene_queue = []
        self._refill_queue()
        self.reset_scene()

    def _refill_queue(self):
        self.scene_queue = list(self.scenes)
        random.shuffle(self.scene_queue)

    def reset_scene(self):
        if not self.scene_queue:
            self._refill_queue()
        self.current_scene = self.scene_queue.pop(0)
        self.start_time = time.time()
        # Randomize colors for each scene run
        self.color1 = self._random_vivid_color()
        self.color2 = self._random_vivid_color()

    def _random_vivid_color(self):
        h = random.random()
        return self._hsl_to_rgb(h * 360, 1.0, 0.5)

    def _hsl_to_rgb(self, h, s, l):
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c/2
        if 0 <= h < 60: r, g, b = c, x, 0
        elif 60 <= h < 120: r, g, b = x, c, 0
        elif 120 <= h < 180: r, g, b = 0, c, x
        elif 180 <= h < 240: r, g, b = 0, x, c
        elif 240 <= h < 300: r, g, b = x, 0, c
        else: r, g, b = c, 0, x
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    async def update(self):
        elapsed = time.time() - self.start_time
        if elapsed > 15:
            self.reset_scene()

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        t = time.time() - self.start_time
        
        if self.current_scene == "moire":
            self._render_moire(draw, t)
        elif self.current_scene == "kaleidoscope":
            self._render_kaleidoscope(img, t)
        elif self.current_scene == "tunnel":
            self._render_tunnel(draw, t)
        elif self.current_scene == "spirograph":
            self._render_spirograph(draw, t)
            
        return img

    def _render_moire(self, draw, t):
        # Two sets of concentric circles moving past each other
        offset = math.sin(t * 2) * 4
        # Set 1
        for r in range(0, 50, 4):
            draw.ellipse([16-r, 16-r, 16+r, 16+r], outline=self.color1)
        # Set 2
        for r in range(0, 50, 4):
            draw.ellipse([16+offset-r, 16-r, 16+offset+r, 16+r], outline=self.color2)

    def _render_kaleidoscope(self, img, t):
        draw = ImageDraw.Draw(img)
        # Draw a small segment and reflect it
        cx, cy = 16, 16
        for i in range(5):
            # Random geometric bit based on time
            x = 16 + math.cos(t + i) * 10
            y = 16 + math.sin(t * 1.5 + i) * 10
            size = 2 + math.sin(t) * 2
            
            # Draw in one octant and reflect
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                # Rotate (x,y) around (cx,cy)
                rx = cx + (x - cx) * math.cos(rad) - (y - cy) * math.sin(rad)
                ry = cy + (x - cx) * math.sin(rad) + (y - cy) * math.cos(rad)
                draw.rectangle([rx-size, ry-size, rx+size, ry+size], fill=self.color1)

    def _render_tunnel(self, draw, t):
        # Infinite zoom effect
        for i in range(10):
            # Size pulses and grows
            size = ((t * 10 + i * 5) % 50)
            color_f = size / 50
            color = (int(self.color1[0]*color_f), int(self.color1[1]*color_f), int(self.color1[2]*color_f))
            draw.rectangle([16-size, 16-size, 16+size, 16+size], outline=color)

    def _render_spirograph(self, draw, t):
        # Hypotrochoid: x = (R-r)cos(th) + d*cos((R-r)/r * th)
        R = 12
        r = 3 + math.sin(t * 0.5) * 2
        d = 8
        points = []
        for th_deg in range(0, 361, 5):
            th = math.radians(th_deg + t * 50)
            x = (R-r)*math.cos(th) + d*math.cos((R-r)/r * th)
            y = (R-r)*math.sin(th) - d*math.sin((R-r)/r * th)
            points.append((16 + x, 16 + y))
        
        if len(points) > 1:
            draw.line(points, fill=self.color2, width=1)
