import random
import io
import time
import httpx
from PIL import Image
from .base import Widget

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon"

class PokemonWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.image = None
        self.last_update = 0
        self.cache_ttl = 15 # Fetch new Pokemon every 15 seconds

    async def fetch_random_pokemon(self):
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                pokemon_id = random.randint(1, 1025)
                url = f"{POKEAPI_URL}/{pokemon_id}"
                
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                sprite_url = data['sprites']['front_default']
                if not sprite_url:
                    return None
                    
                img_response = await client.get(sprite_url)
                img_response.raise_for_status()
                
                return io.BytesIO(img_response.content)
        except Exception as e:
            print(f"Error fetching Pokemon: {e}")
            return None

    async def update(self):
        if time.time() - self.last_update < self.cache_ttl:
            return
            
        img_bytes = await self.fetch_random_pokemon()
        if img_bytes:
            img = Image.open(img_bytes).convert("RGBA")
            
            # Autocrop to remove transparent padding
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Resize to fit the canvas while maintaining aspect ratio
            cw, ch = self.canvas_size
            iw, ih = img.size
            aspect = iw / ih
            if iw > ih:
                new_w, new_h = cw, int(cw / aspect)
            else:
                new_w, new_h = int(ch * aspect), ch
            
            img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
            
            # Center the sprite on the black background
            bg = Image.new("RGB", self.canvas_size, (0, 0, 0))
            offset = ((cw - new_w) // 2, (ch - new_h) // 2)
            bg.paste(img, offset, img)
            self.image = bg
            
        self.last_update = time.time()

    def render(self) -> Image.Image:
        if self.image:
            return self.image
        # Fallback if no image yet
        return Image.new("RGB", self.canvas_size, (0, 0, 0))
