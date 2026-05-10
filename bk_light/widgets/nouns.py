import random
import io
import time
import httpx
from PIL import Image
from .base import Widget

NOUNS_API_URL = "https://noun.pics"

class NounsWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.image = None
        self.last_update = 0
        self.cache_ttl = 15 # Fetch new Noun every 15 seconds

    async def fetch_random_noun(self):
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                noun_id = random.randint(1, 500)
                url = f"{NOUNS_API_URL}/{noun_id}"
                
                response = await client.get(url)
                response.raise_for_status()
                return io.BytesIO(response.content)
        except Exception as e:
            print(f"Error fetching Noun: {e}")
            return None

    async def update(self):
        if time.time() - self.last_update < self.cache_ttl and self.image:
            return
            
        img_data = await self.fetch_random_noun()
        if img_data:
            try:
                img = Image.open(img_data).convert("RGBA")
                
                # Nouns from the web are often scaled up (e.g., 320x320).
                # We MUST resize them back to 32x32 using NEAREST to keep it crisp.
                img = img.resize(self.canvas_size, Image.Resampling.NEAREST)
                
                # Create a black background and paste the noun (handling transparency)
                bg = Image.new("RGB", self.canvas_size, (0, 0, 0))
                
                # Center the noun if it's not full size
                x = (self.canvas_size[0] - img.width) // 2
                y = (self.canvas_size[1] - img.height) // 2
                bg.paste(img, (x, y), img)
                
                self.image = bg
                self.last_update = time.time()
            except Exception as e:
                print(f"Error processing Noun image: {e}")
                # Don't update last_update so we retry sooner
        else:
            # If fetch failed, we'll try again in 5 seconds instead of 15
            self.last_update = time.time() - self.cache_ttl + 5

    def render(self) -> Image.Image:
        if self.image:
            return self.image
        
        # Loading state: a small colorful square in the center
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        center_x, center_y = self.w // 2, self.h // 2
        img.putpixel((center_x, center_y), (255, 0, 0)) # Red dot
        return img
