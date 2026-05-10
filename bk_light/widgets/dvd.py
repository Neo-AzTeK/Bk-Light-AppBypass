import random
import time
from PIL import Image, ImageDraw
from .base import Widget
from bk_light.text import build_text_bitmap
from bk_light.fonts import resolve_font

class DVDWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        
        # Use the requested TINY font
        font_path = resolve_font("tiny")
        self.logo = build_text_bitmap(
            "DVD", 
            font_path, 
            size=6, 
            spacing=0, 
            color=(255, 255, 255), 
            antialias=False
        )
        self.lw, self.lh = self.logo.width, self.logo.height
        
        # Initial position
        self.x = float(random.randint(0, self.w - self.lw))
        self.y = float(random.randint(0, self.h - self.lh))
        
        # SPEED: Max velocity for the display (1 pixel per frame)
        self.dx = 1.0 
        self.dy = 1.0
        
        self.current_color = self._random_color()
        self.flash_timer = 0

    def _random_color(self):
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    async def update(self):
        self.x += self.dx
        self.y += self.dy
        
        hit_x = False
        hit_y = False
        
        # Bounce X
        if self.x <= 0:
            self.x = 0
            self.dx *= -1
            hit_x = True
        elif self.x >= self.w - self.lw:
            self.x = self.w - self.lw
            self.dx *= -1
            hit_x = True
            
        # Bounce Y
        if self.y <= 0:
            self.y = 0
            self.dy *= -1
            hit_y = True
        elif self.y >= self.h - self.lh:
            self.y = self.h - self.lh
            self.dy *= -1
            hit_y = True
            
        if hit_x or hit_y:
            self.current_color = self._random_color()
            if hit_x and hit_y:
                self.flash_timer = 15 # Longer celebration flash

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        
        color = (255, 255, 255) if self.flash_timer > 0 else self.current_color
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        colored_logo = Image.new("RGB", (self.lw, self.lh), color)
        # Paste the colored box through the logo's alpha mask
        img.paste(colored_logo, (int(self.x), int(self.y)), self.logo)
        
        return img
