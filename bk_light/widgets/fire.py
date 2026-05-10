import random
import time
from PIL import Image
from .base import Widget
from bk_light.config import load_config

class FireWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        self.fire_pixels = [0] * (self.w * self.h)
        
        # Load configuration
        config = load_config()
        self.preset = config.presets.fire.get("default")
        
        self.palettes = self.preset.palettes
        self.palette_names = list(self.palettes.keys())
        self.current_palette_idx = 0
        self.last_palette_switch = time.time()
        
        self.cached_palette = []
        self._update_palette()

    def _update_palette(self):
        """Interpolates the small palette from YAML into a full 37-color spectrum."""
        name = self.palette_names[self.current_palette_idx]
        base_colors = self.palettes[name]
        
        if not base_colors or not isinstance(base_colors[0], (list, tuple)):
            base_colors = [[0,0,0], [255,255,255]]
        
        # We need 38 colors (0-37)
        new_palette = []
        for i in range(38):
            idx = (i / 37) * (len(base_colors) - 1)
            c1_idx = int(idx)
            c2_idx = min(c1_idx + 1, len(base_colors) - 1)
            f = idx - c1_idx
            c1 = base_colors[c1_idx]
            c2 = base_colors[c2_idx]
            r = int(c1[0] + (c2[0] - c1[0]) * f)
            g = int(c1[1] + (c2[1] - c1[1]) * f)
            b = int(c1[2] + (c2[2] - c1[2]) * f)
            new_palette.append((r, g, b))
        
        self.cached_palette = new_palette

    async def update(self):
        # Switch palette periodically
        if time.time() - self.last_palette_switch > self.preset.palette_interval:
            self.current_palette_idx = (self.current_palette_idx + 1) % len(self.palette_names)
            self._update_palette()
            self.last_palette_switch = time.time()

        # Optimize: Set bottom row once per update
        bottom_offset = (self.h - 1) * self.w
        for x in range(self.w):
            self.fire_pixels[bottom_offset + x] = random.randint(30, 37)
            
        # Propagation pass
        # We iterate through the array once for speed
        for x in range(self.w):
            for y in range(1, self.h):
                src = y * self.w + x
                pixel = self.fire_pixels[src]
                
                if pixel == 0:
                    self.fire_pixels[src - self.w] = 0
                else:
                    # Doom fire jitter
                    rand = random.randint(0, 3)
                    dst = src - self.w - rand + 1
                    # Boundary check and higher decay
                    if 0 <= dst < len(self.fire_pixels):
                        # Increased decay: random 0-3 instead of 0-2
                        decay = random.randint(0, 3)
                        self.fire_pixels[dst] = max(0, pixel - decay)

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        # Map indices to RGB tuples
        pixels = [self.cached_palette[p] for p in self.fire_pixels]
        img.putdata(pixels)
        return img
