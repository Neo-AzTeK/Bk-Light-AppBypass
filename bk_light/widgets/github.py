import random
import time
import httpx
import re
import math
from PIL import Image, ImageDraw
from .base import Widget
from bk_light.config import load_config
from bk_light.text import build_text_bitmap
from bk_light.fonts import resolve_font

class GithubWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        # Full year grid: 53 weeks * 7 days
        self.full_history = [[(0, 0, 0)] * 7 for _ in range(53)]
        
        # Load configuration
        config = load_config()
        self.preset = config.presets.github.get("default")
        self.username = self.preset.username
        
        self.last_update = 0
        self.cache_ttl = self.preset.cache_ttl
        self.scroll_offset = 0.0
        
        # Pre-render username with the new TINY font
        # We assume tiny.ttf is a 5-6px tall font
        font_path = resolve_font("tiny")
        self.name_bitmap = build_text_bitmap(
            self.username, 
            font_path, 
            size=6, # Optimized for the 'tiny' font style
            spacing=0, 
            color=(255, 255, 255), 
            antialias=False
        )

    async def update(self):
        # 1. Update Data (Every Hour)
        if time.time() - self.last_update > self.cache_ttl:
            await self._fetch_data()

        # 2. Update Scroll
        # Scroll smoothly. 1 column of 3px every ~1.5 seconds
        self.scroll_offset += 0.03
        if self.scroll_offset >= 53:
            self.scroll_offset = 0

    async def _fetch_data(self):
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://github.com/users/{self.username}/contributions"
                resp = await client.get(url)
                html = resp.text
                
                # Extract level (0-4)
                levels = re.findall(r'data-level="(\d)"', html)

                if levels:
                    # Last 53 weeks (full year)
                    levels = levels[-371:]
                    color_map = {str(k): tuple(v) for k, v in self.preset.colors.items()}
                    
                    for i, level in enumerate(levels):
                        col = i // 7
                        row = i % 7
                        if col < 53:
                            self.full_history[col][row] = color_map.get(level, (0, 0, 0))
                
                self.last_update = time.time()
        except Exception as e:
            print(f"Error fetching GitHub contributions: {e}")

    def render(self) -> Image.Image:
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        
        # 1. Render Username at the top
        name_x = (32 - self.name_bitmap.width) // 2
        img.paste(self.name_bitmap, (max(0, name_x), 2), self.name_bitmap)
        
        # 2. Render Scrolling Graph
        # With 3x3 blocks, we can fit ~10.6 weeks on screen at once
        block_size = 3
        start_y = 10 # Adjusted to start after the name
        
        # We render column by column
        for x_block in range(12): # 12 blocks * 3px = 36px (allows for partial scrolling)
            # Find which week this block corresponds to
            week_idx = (int(self.scroll_offset) + x_block) % 53
            
            # Precise horizontal position with fractional scrolling
            x_pos = int(x_block * block_size - (self.scroll_offset % 1) * block_size)
            
            if x_pos >= 32 or x_pos < -block_size:
                continue

            for row in range(7):
                color = self.full_history[week_idx][row]
                
                # Sparkle logic for Level 4
                if color == tuple(self.preset.colors.get("4", [0,255,0])):
                    if (time.time() * 8 + week_idx + row) % 15 < 1:
                        color = (180, 255, 180)

                # Draw the 3x3 block (clamped to screen)
                y_pos = start_y + row * block_size
                for dy in range(block_size):
                    for dx in range(block_size):
                        target_x = x_pos + dx
                        target_y = y_pos + dy
                        if 0 <= target_x < 32 and 0 <= target_y < 32:
                            img.putpixel((target_x, target_y), color)
                
        return img
