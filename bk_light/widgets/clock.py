import time
from datetime import datetime
from PIL import Image
import sys
from pathlib import Path
from .base import Widget

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.text import build_text_bitmap
from bk_light.fonts import resolve_font

class ClockWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.font_path = resolve_font("ipixel")

    async def update(self):
        pass

    def render(self) -> Image.Image:
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        
        now = datetime.now()
        hours = f"{now.hour:02d}"
        minutes = f"{now.minute:02d}"
        show_colon = int(time.time()) % 2 == 0
        
        # To prevent jitter, we render hours and minutes separately 
        # but we use a fixed-width "dummy" colon if it's off.
        # Even better: render the full "HH:MM" but just make the colon black when hidden.
        # However, build_text_bitmap doesn't support per-character colors easily.
        
        # SOLUTION: Create the "HH:MM" bitmap once, then just paste it.
        # To ensure the width is ALWAYS the same, we always use ":" in the string calculation.
        full_time_str = f"{hours}:{minutes}"
        text_bmp = build_text_bitmap(full_time_str, self.font_path, 8, 1, (255, 255, 255), False, True)
        
        # Center horizontally and vertically
        x = (self.canvas_size[0] - text_bmp.width) // 2
        y = (self.canvas_size[1] - text_bmp.height) // 2
        
        if not show_colon:
            # If colon should be hidden, we draw the HH:MM but then "black out" the colon area.
            # In ipixel size 8, the colon is usually in the middle.
            # Let's just render HH and MM separately but at the exact positions they would be in "HH:MM"
            hours_bmp = build_text_bitmap(hours, self.font_path, 8, 1, (255, 255, 255), False, True)
            minutes_bmp = build_text_bitmap(minutes, self.font_path, 8, 1, (255, 255, 255), False, True)
            
            # Draw hours at the start of where the full string would be
            img.paste(hours_bmp, (x, y), hours_bmp)
            # Draw minutes at the end of where the full string would be
            img.paste(minutes_bmp, (x + text_bmp.width - minutes_bmp.width, y), minutes_bmp)
        else:
            img.paste(text_bmp, (x, y), text_bmp)
        
        return img
