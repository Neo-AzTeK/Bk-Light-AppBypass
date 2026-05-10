import psutil
from PIL import Image, ImageDraw
import sys
from pathlib import Path
from .base import Widget

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.text import build_text_bitmap
from bk_light.fonts import resolve_font

class SystemWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.cpu_percent = 0
        self.ram_percent = 0
        self.font_path = resolve_font("ipixel")

    async def update(self):
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent

    def render(self) -> Image.Image:
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        w, h = self.canvas_size
        
        # Baselines (High contrast)
        draw.line([2, h - 2, 10, h - 2], fill=(0, 0, 128))
        draw.line([14, h - 2, 22, h - 2], fill=(128, 0, 128))
        
        # CPU Bar (Cyan for high contrast)
        cpu_h = int((self.cpu_percent / 100) * (h - 14)) # Reserve top 10px for text
        if cpu_h > 0:
            draw.rectangle([2, h - 3 - cpu_h, 10, h - 3], fill=(0, 255, 255))
        
        # RAM Bar (Magenta for high contrast)
        ram_h = int((self.ram_percent / 100) * (h - 14))
        if ram_h > 0:
            draw.rectangle([14, h - 3 - ram_h, 22, h - 3], fill=(255, 0, 255))
        
        # Numeric Readouts
        cpu_text = f"{int(self.cpu_percent)}"
        ram_text = f"{int(self.ram_percent)}"
        
        cpu_bmp = build_text_bitmap(cpu_text, self.font_path, 8, 1, (255, 255, 255), False, True)
        ram_bmp = build_text_bitmap(ram_text, self.font_path, 8, 1, (255, 255, 255), False, True)
        
        img.paste(cpu_bmp, (2, 0), cpu_bmp)
        img.paste(ram_bmp, (14, 0), ram_bmp)
        
        return img
