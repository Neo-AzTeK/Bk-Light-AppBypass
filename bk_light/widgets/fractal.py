import time
import math
import random
from PIL import Image
from .base import Widget

class FractalWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        
        # Scenario = (type, center_x, center_y, param_c_or_none)
        self.scenarios = [
            # Mandelbrot Classics
            ("mandelbrot", -0.743643887037158, 0.131825904205311, None),
            ("mandelbrot", -1.74966341794, 0.0, None),
            ("mandelbrot", -0.16070135, 1.0375665, None),
            
            # Julia Sets
            ("julia", 0, 0, complex(-0.7, 0.27015)),
            ("julia", 0, 0, complex(0.355, 0.355)),
            ("julia", 0, 0, complex(-0.8, 0.156)),
            ("julia", 0, 0, complex(-0.4, 0.6)),
            
            # Burning Ship
            ("burning_ship", -1.75, -0.03, None),
            ("burning_ship", -1.25, 0.0, None)
        ]
        
        self.scenario_queue = []
        self._refill_queue()
        self.reset_simulation()

    def _refill_queue(self):
        self.scenario_queue = list(self.scenarios)
        random.shuffle(self.scenario_queue)

    def reset_simulation(self):
        if not self.scenario_queue:
            self._refill_queue()
            
        self.current_scenario = self.scenario_queue.pop(0)
        self.f_type, self.cx, self.cy, self.param_c = self.current_scenario
        
        self.zoom = 1.0
        self.start_time = time.time()
        self.max_iter = 32

    async def update(self):
        elapsed = time.time() - self.start_time
        # Zoom exponentially
        self.zoom = 1.0 + (elapsed * 0.5)**2
        
        if elapsed > 15: # Rotate faster than GoL
            self.reset_simulation()

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        
        view_w = 3.0 / self.zoom
        view_h = view_w * (self.h / self.w)
        
        xmin, xmax = self.cx - view_w/2, self.cx + view_w/2
        ymin, ymax = self.cy - view_h/2, self.cy + view_h/2
        
        pixels = []
        for y in range(self.h):
            y0 = ymin + (y / self.h) * (ymax - ymin)
            for x in range(self.w):
                x0 = xmin + (x / self.w) * (xmax - xmin)
                
                iteration = 0
                if self.f_type == "julia":
                    zx, zy = x0, y0
                    c = self.param_c
                else: # mandelbrot or burning ship
                    zx, zy = 0, 0
                    c = complex(x0, y0)
                
                while zx*zx + zy*zy <= 4 and iteration < self.max_iter:
                    if self.f_type == "burning_ship":
                        xtemp = zx*zx - zy*zy + c.real
                        zy = abs(2*zx*zy) + c.imag
                        zx = xtemp
                    else: # mandelbrot or julia
                        xtemp = zx*zx - zy*zy + c.real
                        zy = 2*zx*zy + c.imag
                        zx = xtemp
                    iteration += 1
                
                if iteration == self.max_iter:
                    pixels.append((0, 0, 0))
                else:
                    hue = (iteration / self.max_iter) * 360 + (time.time() * 20) % 360
                    r, g, b = self._hsl_to_rgb(hue, 1.0, 0.5)
                    pixels.append((r, g, b))
        
        img.putdata(pixels)
        return img

    def _hsl_to_rgb(self, h, s, l):
        h = h % 360
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
