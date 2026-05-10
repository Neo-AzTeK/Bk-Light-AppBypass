import random
from PIL import Image, ImageDraw
from .base import Widget

class PipesWidget(Widget):
    """
    A Windows 3D Pipes screensaver homage.
    Generates twisting, turning colored pipes that fill the screen.
    """
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        self.grid_w = self.w // 2
        self.grid_h = self.h // 2
        self.image = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        self.occupied = set()
        
        self.current_pipe = None
        self.reset_timer = 0
        self.max_pipes = 15
        self.pipe_count = 0

    def _get_random_color(self):
        # Classic bright Windows pipe colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
            (192, 192, 192),# Silver
        ]
        return random.choice(colors)

    def _start_new_pipe(self):
        # Find an unoccupied start point
        attempts = 0
        while attempts < 50:
            x = random.randint(0, self.grid_w - 1)
            y = random.randint(0, self.grid_h - 1)
            if (x, y) not in self.occupied:
                color = self._get_random_color()
                direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.current_pipe = {
                    "x": x,
                    "y": y,
                    "dir": direction,
                    "color": color
                }
                self.occupied.add((x, y))
                self.pipe_count += 1
                return True
            attempts += 1
        return False

    async def update(self):
        if len(self.occupied) > (self.grid_w * self.grid_h * 0.7) or self.pipe_count > self.max_pipes:
            self.reset_timer += 1
            if self.reset_timer > 40:
                self.image = Image.new("RGB", (self.w, self.h), (0, 0, 0))
                self.occupied = set()
                self.reset_timer = 0
                self.pipe_count = 0
                self.current_pipe = None
            return

        if self.current_pipe is None:
            if not self._start_new_pipe():
                # Screen is full
                return

        p = self.current_pipe
        
        # Draw the current segment
        # We use a 2x2 area for the pipe look
        px, py = p["x"] * 2, p["y"] * 2
        base_color = p["color"]
        highlight = tuple(min(255, c + 100) for c in base_color)
        shadow = tuple(max(0, c - 100) for c in base_color)
        
        # 3D shading:
        # TL: Highlight, TR/BL: Base, BR: Shadow
        self.image.putpixel((px, py), highlight)
        self.image.putpixel((px + 1, py), base_color)
        self.image.putpixel((px, py + 1), base_color)
        self.image.putpixel((px + 1, py + 1), shadow)
        
        # Decide next move
        # 20% chance to change direction
        if random.random() < 0.2:
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            # Don't go backwards
            back = (-p["dir"][0], -p["dir"][1])
            dirs.remove(back)
            p["dir"] = random.choice(dirs)
            
        nx, ny = p["x"] + p["dir"][0], p["y"] + p["dir"][1]
        
        # Collision check
        if 0 <= nx < self.grid_w and 0 <= ny < self.grid_h and (nx, ny) not in self.occupied:
            p["x"], p["y"] = nx, ny
            self.occupied.add((nx, ny))
        else:
            self.current_pipe = None

    def render(self) -> Image.Image:
        return self.image
