import time
import httpx
from PIL import Image, ImageDraw
from .base import Widget
from bk_light.config import load_config
from bk_light.text import build_text_bitmap
from bk_light.fonts import resolve_font

class WeatherWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        config = load_config()
        self.preset = config.presets.weather.get("default")
        
        self.lat = self.preset.latitude
        self.lon = self.preset.longitude
        self.city = self.preset.city
        
        self.temp = "--"
        self.condition = "loading"
        self.last_update = 0
        self.cache_ttl = self.preset.cache_ttl
        self.font_path = resolve_font("ipixel")

    async def update(self):
        if time.time() - self.last_update < self.cache_ttl:
            return
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current_weather=true"
                resp = await client.get(url)
                data = resp.json()
                if "current_weather" in data:
                    cw = data["current_weather"]
                    self.temp = f"{int(round(cw['temperature']))}"
                    self.condition = self._get_condition(cw["weathercode"])
                self.last_update = time.time()
        except Exception as e:
            print(f"Error fetching weather: {e}")

    def _get_condition(self, code):
        if code == 0: return "clear"
        if code in [1, 2, 3]: return "cloudy"
        if code in [45, 48]: return "fog"
        if code in [51, 53, 55, 61, 63, 65]: return "rain"
        if code in [71, 73, 75, 77]: return "snow"
        if code in [95, 96, 99]: return "storm"
        return "cloudy"

    def render(self) -> Image.Image:
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Draw Icon (Top Half)
        # Use high-saturation colors for LEDs
        if self.condition == "clear":
            draw.ellipse([8, 2, 22, 16], fill=(255, 255, 0)) # Sun
        elif self.condition == "cloudy":
            draw.ellipse([6, 6, 18, 14], fill=(200, 200, 200)) # Cloud base
            draw.ellipse([14, 4, 24, 16], fill=(255, 255, 255)) # Cloud puff
        elif self.condition == "rain":
            draw.ellipse([6, 4, 24, 12], fill=(150, 150, 150))
            draw.line([10, 14, 10, 18], fill=(0, 255, 255)) # Cyan rain
            draw.line([16, 14, 16, 18], fill=(0, 255, 255))
            draw.line([22, 14, 22, 18], fill=(0, 255, 255))
        else: # Fallback storm/fog etc
            draw.ellipse([6, 4, 24, 12], fill=(200, 200, 200))
            
        # 2. Draw Temp (Bottom Half)
        temp_text = f"{self.temp}°"
        # Use ipixel font size 8
        temp_bmp = build_text_bitmap(temp_text, self.font_path, 8, 1, (0, 255, 255), False, True)
        
        # Center horizontally, place at bottom
        x = (self.canvas_size[0] - temp_bmp.width) // 2
        y = 20
        img.paste(temp_bmp, (x, y), temp_bmp)
        
        return img
