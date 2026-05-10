import random
from PIL import Image, ImageDraw
from .base import Widget

class MatrixRainWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        w, h = canvas_size
        self.drops = [random.randint(-h, 0) for _ in range(w)]

    async def update(self):
        w, h = self.canvas_size
        for i in range(w):
            if self.drops[i] * 1 > h and random.random() > 0.8:
                self.drops[i] = 0
            self.drops[i] += 1

    def render(self) -> Image.Image:
        w, h = self.canvas_size
        img = Image.new("RGB", (w, h), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for i in range(w):
            y = self.drops[i]
            # Draw tail
            for tail in range(4):
                if 0 <= y - tail < h:
                    intensity = max(0, 255 - (tail * 60))
                    draw.point((i, y - tail), fill=(0, intensity, 0))
                    
            # Draw bright head
            if 0 <= y < h:
                draw.point((i, y), fill=(150, 255, 150))
                
        return img
