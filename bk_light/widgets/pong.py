import random
from PIL import Image, ImageDraw
from .base import Widget

class PongWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        w, h = canvas_size
        self.ball = [float(w//2), float(h//2)]
        self.ball_vel = [1.2, 0.5]
        self.p1_y = float(h//2 - 3)
        self.p2_y = float(h//2 - 3)
        self.p_size = 6
        
        # Human-like AI state
        self.p1_target_y = self.p1_y
        self.p2_target_y = self.p2_y

    async def update(self):
        w, h = self.canvas_size
        
        # Move ball
        self.ball[0] += self.ball_vel[0]
        self.ball[1] += self.ball_vel[1]
        
        # Wall bounce (top/bottom)
        if self.ball[1] <= 0:
            self.ball[1] = 0
            self.ball_vel[1] = abs(self.ball_vel[1])
        elif self.ball[1] >= h - 1:
            self.ball[1] = h - 1
            self.ball_vel[1] = -abs(self.ball_vel[1])
            
        # Paddle AI - Player 1 (Left)
        # Smooth pursuit with some lag
        if self.ball[0] < w * 0.7:
            if random.random() < 0.15:
                self.p1_target_y = self.ball[1] - (self.p_size / 2) + random.uniform(-1, 1)
            
            # Move towards target
            if self.p1_y + self.p_size/2 < self.p1_target_y + self.p_size/2 - 0.5:
                self.p1_y += 0.6
            elif self.p1_y + self.p_size/2 > self.p1_target_y + self.p_size/2 + 0.5:
                self.p1_y -= 0.6

        # Paddle AI - Player 2 (Right)
        if self.ball[0] > w * 0.3:
            if random.random() < 0.15:
                self.p2_target_y = self.ball[1] - (self.p_size / 2) + random.uniform(-1, 1)
                
            if self.p2_y + self.p_size/2 < self.p2_target_y + self.p_size/2 - 0.5:
                self.p2_y += 0.6
            elif self.p2_y + self.p_size/2 > self.p2_target_y + self.p_size/2 + 0.5:
                self.p2_y -= 0.6
        
        # Clamp paddles
        self.p1_y = max(0, min(h - self.p_size, self.p1_y))
        self.p2_y = max(0, min(h - self.p_size, self.p2_y))
        
        # Paddle bounce logic with position correction to prevent "tunneling"
        # Player 1 (Left)
        if self.ball_vel[0] < 0 and self.ball[0] <= 2.0:
            if self.p1_y - 1 <= self.ball[1] <= self.p1_y + self.p_size + 1:
                self.ball[0] = 2.1 # Snap back to front of paddle
                self.ball_vel[0] = abs(self.ball_vel[0])
                # Speed up slightly on hit
                self.ball_vel[0] = min(2.0, self.ball_vel[0] * 1.05)
                # Spin
                hit_pos = (self.ball[1] - (self.p1_y + self.p_size/2)) / (self.p_size/2)
                self.ball_vel[1] += hit_pos * 0.8
            
        # Player 2 (Right)
        if self.ball_vel[0] > 0 and self.ball[0] >= w - 3.0:
            if self.p2_y - 1 <= self.ball[1] <= self.p2_y + self.p_size + 1:
                self.ball[0] = w - 3.1
                self.ball_vel[0] = -abs(self.ball_vel[0])
                self.ball_vel[0] = max(-2.0, self.ball_vel[0] * 1.05)
                # Spin
                hit_pos = (self.ball[1] - (self.p2_y + self.p_size/2)) / (self.p_size/2)
                self.ball_vel[1] += hit_pos * 0.8
            
        # Clamp vertical velocity
        self.ball_vel[1] = max(-1.5, min(1.5, self.ball_vel[1]))
            
        # Score reset
        if self.ball[0] < -1 or self.ball[0] > w + 1:
            self.ball = [float(w//2), float(h//2)]
            # Faster reset serve
            self.ball_vel = [random.choice([-1.2, 1.2]), random.uniform(-0.5, 0.5)]

    def render(self) -> Image.Image:
        img = Image.new("RGB", self.canvas_size, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        w, h = self.canvas_size
        
        # Center line
        for i in range(0, h, 4):
            draw.point((w//2, i), fill=(50, 50, 50))
        
        # Paddles (solid white)
        draw.line([1, int(self.p1_y), 1, int(self.p1_y + self.p_size)], fill=(255, 255, 255))
        draw.line([w-2, int(self.p2_y), w-2, int(self.p2_y + self.p_size)], fill=(255, 255, 255))
        
        # Ball
        draw.point((int(self.ball[0]), int(self.ball[1])), fill=(255, 255, 255))
        
        return img
