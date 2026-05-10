import random
import math
from PIL import Image, ImageDraw
from .base import Widget

class NyanWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        self.frame = 0
        
        # Colors
        self.C_GREY = (153, 153, 153)
        self.C_TAN = (255, 204, 153)
        self.C_PINK = (255, 51, 153)
        self.C_DPINK = (255, 0, 153)
        self.C_BLACK = (0, 0, 0)
        self.C_WHITE = (255, 255, 255)
        
        self.RAINBOW = [
            (255, 0, 0),      # Red
            (255, 153, 0),    # Orange
            (255, 255, 0),    # Yellow
            (51, 255, 0),     # Green
            (0, 153, 255),    # Blue
            (102, 51, 255),   # Purple
        ]

        # Stars: (x, y, type)
        self.stars = []
        for _ in range(15):
            self.stars.append([random.randint(0, self.w-1), random.randint(0, self.h-1), random.randint(0, 2)])

        # Cat position (fixed center-ish, but bobbing)
        self.cat_x = (self.w // 2) - 5
        self.cat_y = (self.h // 2) - 5
        
        # Trail history to create the wave
        # We store the Y offset for each X position behind the cat
        self.trail_offsets = [0] * self.w

    async def update(self):
        self.frame += 1
        
        # Update stars
        for i in range(len(self.stars)):
            self.stars[i][0] -= 1 # Scroll left
            if self.stars[i][0] < 0:
                self.stars[i][0] = self.w - 1
                self.stars[i][1] = random.randint(0, self.h - 1)
        
        # Bobbing animation (sine wave)
        # Nyan Cat bobs up and down every few frames
        self.bob = 1 if (self.frame // 4) % 2 == 0 else 0
        
        # Update trail offsets (shift and add new)
        # The trail follows the cat's bobbing but with a delay (wave)
        current_y_offset = self.bob
        self.trail_offsets.pop()
        self.trail_offsets.insert(0, current_y_offset)

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 51)) # Dark blue space
        draw = ImageDraw.Draw(img)
        
        # Draw Stars
        for sx, sy, stype in self.stars:
            color = self.C_WHITE
            if stype == 1 and (self.frame // 2) % 2 == 0:
                # Flickering star
                continue
            img.putpixel((int(sx), int(sy)), color)

        # Draw Rainbow Trail
        # The trail is 6 pixels high, each color is 1 pixel
        # It should be behind the cat (left of cat_x)
        trail_start_x = 0
        trail_end_x = int(self.cat_x) + 2
        
        for x in range(trail_start_x, trail_end_x):
            # Calculate wave offset for this X
            # We want it to look like it's connected to the cat
            # The cat's body is at cat_y + bob
            # The trail's Y position depends on how far back it is
            dist_from_cat = trail_end_x - x
            offset_idx = dist_from_cat % len(self.trail_offsets)
            y_offset = self.trail_offsets[offset_idx]
            
            # Draw the 6 colors
            base_y = self.cat_y + 2 + y_offset
            for i, color in enumerate(self.RAINBOW):
                ty = int(base_y + i)
                if 0 <= ty < self.h and 0 <= x < self.w:
                    img.putpixel((x, ty), color)

        # Draw Nyan Cat (10x10)
        cx = int(self.cat_x)
        cy = int(self.cat_y) + self.bob
        
        # 1. Tail (wiggles)
        tx = cx - 1
        ty = cy + 3
        twiggle = 1 if (self.frame // 4) % 2 == 0 else 0
        img.putpixel((tx, ty + twiggle), self.C_GREY)
        img.putpixel((tx-1, ty + twiggle), self.C_GREY)
        
        # 2. Body (Pop-Tart) 7x6
        # Crust
        draw.rectangle([cx+1, cy+1, cx+7, cy+6], fill=self.C_TAN)
        # Frosting
        draw.rectangle([cx+2, cy+2, cx+6, cy+5], fill=self.C_PINK)
        # Sprinkles (dots)
        img.putpixel((cx+3, cy+3), self.C_DPINK)
        img.putpixel((cx+5, cy+3), self.C_DPINK)
        img.putpixel((cx+4, cy+4), self.C_DPINK)
        img.putpixel((cx+6, cy+5), self.C_DPINK)
        img.putpixel((cx+2, cy+5), self.C_DPINK)

        # 3. Head (moves with body)
        hx, hy = cx + 6, cy + 2
        # Ears
        img.putpixel((hx+1, hy-1), self.C_GREY)
        img.putpixel((hx+3, hy-1), self.C_GREY)
        # Face
        draw.rectangle([hx, hy, hx+4, hy+3], fill=self.C_GREY)
        # Eyes
        img.putpixel((hx+1, hy+1), self.C_BLACK)
        img.putpixel((hx+3, hy+1), self.C_BLACK)
        # Mouth/Nose
        img.putpixel((hx+2, hy+2), self.C_BLACK)
        
        # 4. Legs
        # Front legs
        img.putpixel((cx+2, cy+7), self.C_GREY)
        img.putpixel((cx+3, cy+7), self.C_GREY)
        # Back legs
        img.putpixel((cx+6, cy+7), self.C_GREY)
        img.putpixel((cx+7, cy+7), self.C_GREY)

        return img
