import random
import io
import time
import httpx
from PIL import Image
from .base import Widget

class RosesWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.image = None
        self.last_update = 0
        self.cache_ttl = 30 # Fetch a new rose every 30 seconds

    async def fetch_random_rose(self):
        try:
            # LoremFlickr is a great keyless API for random themed images
            url = "https://loremflickr.com/32/32/rose"
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return io.BytesIO(response.content)
        except Exception as e:
            print(f"Error fetching rose: {e}")
            return None

    async def update(self):
        if time.time() - self.last_update < self.cache_ttl:
            return
            
        img_bytes = await self.fetch_random_rose()
        if img_bytes:
            try:
                img = Image.open(img_bytes).convert("RGB")
                # Ensure it's exactly 32x32 (LoremFlickr usually handles this but safety first)
                if img.size != self.canvas_size:
                    img = img.resize(self.canvas_size, Image.Resampling.LANCZOS)
                self.image = img
            except Exception as e:
                print(f"Error processing rose image: {e}")
            
        self.last_update = time.time()

    def render(self) -> Image.Image:
        if self.image:
            return self.image
        # Fallback to black if no image yet
        return Image.new("RGB", self.canvas_size, (0, 0, 0))
