import random
import time
import math
from PIL import Image
from .base import Widget
from bk_light.config import load_config

# Famous Symmetrical & Large Game of Life Patterns
PATTERNS = {
    "pulsar": [
        [0,0,1,1,1,0,0,0,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [0,0,1,1,1,0,0,0,1,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,1,1,0,0,0,1,1,1,0,0],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [1,0,0,0,0,1,0,1,0,0,0,0,1],
        [0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,1,1,1,0,0,0,1,1,1,0,0]
    ],
    "koks_galaxy": [
        [1,1,0,1,1,1,1,1,1],
        [1,1,0,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,0,1,1],
        [1,1,1,1,1,1,0,1,1]
    ],
    "pinwheel": [
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,0,1,1],
        [1,1,0,0,0,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0]
    ],
    "cloverleaf": [
        [0,0,0,0,1,0,0,0,0],
        [0,0,0,1,0,1,0,0,0],
        [0,0,1,0,0,0,1,0,0],
        [0,1,0,1,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,1],
        [0,1,0,1,0,1,0,1,0],
        [0,0,1,0,0,0,1,0,0],
        [0,0,0,1,0,1,0,0,0],
        [0,0,0,0,1,0,0,0,0]
    ],
    "acorn": [
        [0,1,0,0,0,0,0],
        [0,0,0,1,0,0,0],
        [1,1,0,0,1,1,1]
    ],
    "copperhead": [
        [0,0,0,1,1,0,0,0],
        [0,0,1,1,1,1,0,0],
        [1,0,1,0,0,1,0,1],
        [1,0,0,0,0,0,0,1],
        [0,1,0,0,0,0,1,0],
        [0,1,0,1,1,0,1,0],
        [0,0,1,0,0,1,0,0],
        [0,0,0,1,1,0,0,0]
    ],
    "queen_bee": [
        [1,1,0,0,0,0,0],
        [0,0,1,0,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,0,1,0,0],
        [0,0,0,1,0,0,0],
        [0,0,1,0,0,0,0],
        [1,1,0,0,0,0,0]
    ],
    "glider_gun": [
        [1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0]
    ]
}

def create_grid_from_name(name, width, height):
    grid = [[0] * width for _ in range(height)]
    pattern = PATTERNS[name]
    px = (width - len(pattern[0])) // 2
    py = (height - len(pattern)) // 2
    flip_h = random.choice([True, False])
    flip_v = random.choice([True, False])
    for y, row in enumerate(pattern):
        for x, val in enumerate(row):
            if val:
                target_y = (py + (len(pattern) - 1 - y if flip_v else y)) % height
                target_x = (px + (len(row) - 1 - x if flip_h else x)) % width
                grid[target_y][target_x] = 1
    return grid

def get_next_generation(grid):
    height = len(grid)
    width = len(grid[0])
    new_grid = [[0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            neighbors = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0: continue
                    ny, nx = (y + dy) % height, (x + dx) % width
                    neighbors += (1 if grid[ny][nx] > 0 else 0)
            if grid[y][x] > 0:
                if neighbors in [2, 3]:
                    new_grid[y][x] = min(100, grid[y][x] + 1)
            else:
                if neighbors == 3:
                    new_grid[y][x] = 1
    return new_grid

class GameOfLifeWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.pattern_queue = []
        self._refill_queue()
        
        self.grid = self._pop_and_create_grid()
        self.history = [] 
        self.max_history = 3
        
        config = load_config()
        self.preset = config.presets.game_of_life.get("default")
        self.stagnation_counter = 0
        self.start_time = time.time()

    def _refill_queue(self):
        self.pattern_queue = list(PATTERNS.keys())
        random.shuffle(self.pattern_queue)

    def _pop_and_create_grid(self):
        if not self.pattern_queue:
            self._refill_queue()
        name = self.pattern_queue.pop(0)
        return create_grid_from_name(name, self.canvas_size[0], self.canvas_size[1])

    async def update(self):
        self.history.insert(0, [row[:] for row in self.grid])
        if len(self.history) > self.max_history: self.history.pop()
        new_grid = get_next_generation(self.grid)
        
        if self._grids_equal(new_grid, self.grid): self.stagnation_counter += 1
        else: self.stagnation_counter = 0
        
        total_alive = sum(sum(1 for cell in row if cell > 0) for row in new_grid)
        time_elapsed = time.time() - self.start_time
        
        if (total_alive < 3 or 
            self.stagnation_counter > self.preset.stagnation_limit or 
            time_elapsed > self.preset.max_simulation_time):
            
            self.grid = self._pop_and_create_grid()
            self.stagnation_counter = 0
            self.start_time = time.time()
            self.history = []
        else:
            self.grid = new_grid

    def _grids_equal(self, g1, g2):
        if g1 is None or g2 is None: return False
        for y in range(len(g1)):
            for x in range(len(g1[0])):
                if (g1[y][x] > 0) != (g2[y][x] > 0): return False
        return True

    def render(self) -> Image.Image:
        w, h = self.canvas_size
        img = Image.new("RGB", (w, h), (0, 0, 0))
        for i, prev_grid in enumerate(self.history):
            alpha = 1.0 - ((i + 1) / (self.max_history + 1))
            trail_color = (int(0 * alpha), int(80 * alpha), int(200 * alpha))
            for y in range(h):
                for x in range(w):
                    if prev_grid[y][x] > 0 and self.grid[y][x] == 0:
                        current = img.getpixel((x, y))
                        new_color = (max(current[0], trail_color[0]), max(current[1], trail_color[1]), max(current[2], trail_color[2]))
                        img.putpixel((x, y), new_color)
        hue_offset = (time.time() * 45) % 360
        c1 = self.preset.new_cell_color
        max_age = self.preset.max_age
        for y in range(h):
            for x in range(w):
                age = self.grid[y][x]
                if age > 0:
                    f = min(1.0, (age - 1) / max_age)
                    target_r, target_g, target_b = self._hsl_to_rgb(hue_offset, 1.0, 0.5)
                    r = int(c1[0] + (target_r - c1[0]) * f)
                    g = int(c1[1] + (target_g - c1[1]) * f)
                    b = int(c1[2] + (target_b - c1[2]) * f)
                    img.putpixel((x, y), (r, g, b))
        return img

    def _hsl_to_rgb(self, h, s, l):
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c/2
        if 0 <= h < 60: r, g, b = c, x, 0
        elif 60 <= h < 120: r, g, b = x, c, 0
        elif 120 <= h < 180: r, g, b = 0, c, x
        elif 180 <= h < 240: r, g, b = 0, x, c
        elif 240 <= h < 300: r, g, b = x, 0, c
        else: r, g, b = c, 0, x
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
