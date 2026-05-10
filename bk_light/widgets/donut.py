import math
from PIL import Image, ImageDraw
from .base import Widget

class DonutWidget(Widget):
    """
    A 3D Spinning Donut (Torus) widget inspired by donut.c.
    Renders a spinning torus with basic pixel shading.
    """
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        self.A = 0.0 # Rotation around X axis
        self.B = 0.0 # Rotation around Z axis
        
        # Precompute constants
        self.R1 = 1.0  # radius of the circle
        self.R2 = 2.0  # radius of the torus
        self.K2 = 5.0  # distance from viewer to torus
        
        # K1: distance from viewer to screen
        # On a 32x32 screen, we want the donut to fill most of the space
        self.K1 = self.w * self.K2 * 3 / (8 * (self.R1 + self.R2))

    async def update(self):
        # Update rotations
        self.A += 0.07
        self.B += 0.03

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        
        # Z-buffer and output character buffer (luminance)
        z_buffer = [0.0] * (self.w * self.h)
        
        cosA = math.cos(self.A)
        sinA = math.sin(self.A)
        cosB = math.cos(self.B)
        sinB = math.sin(self.B)

        # Iterate through the torus surface
        # theta goes around the cross-sectional circle of the torus
        # phi goes around the center of the torus
        theta = 0
        while theta < 2 * math.pi:
            costheta = math.cos(theta)
            sintheta = math.sin(theta)
            
            phi = 0
            while phi < 2 * math.pi:
                cosphi = math.cos(phi)
                sinphi = math.sin(phi)
                
                # 3D coordinates before rotation
                # (R2 + R1*cos(theta)) is the distance from the center of the torus
                circle_x = self.R2 + self.R1 * costheta
                circle_y = self.R1 * sintheta
                
                # 3D coordinates after rotations A and B
                x = circle_x * (cosB * cosphi + sinA * sinB * sinphi) - circle_y * cosA * sinB
                y = circle_x * (sinB * cosphi - sinA * cosB * sinphi) + circle_y * cosA * cosB
                z = self.K2 + cosA * circle_x * sinphi + circle_y * sinA
                ooz = 1 / z # "one over z"
                
                # Projection to 2D screen
                xp = int(self.w / 2 + self.K1 * ooz * x)
                yp = int(self.h / 2 - self.K1 * ooz * y)
                
                # Shading (luminance)
                # L is the dot product of the normal and a light source vector (0, 1, -1)
                L = (cosphi * costheta * sinB - cosA * costheta * sinphi -
                     sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi))
                
                # L ranges from -sqrt(2) to sqrt(2). If L > 0, the surface is lit.
                if L > 0:
                    if 0 <= xp < self.w and 0 <= yp < self.h:
                        idx = xp + yp * self.w
                        if ooz > z_buffer[idx]:
                            z_buffer[idx] = ooz
                            # Map L (roughly 0 to 1.4) to brightness (0 to 255)
                            # We use a slight multiplier to make it pop
                            brightness = int(L * 180)
                            brightness = min(255, max(0, brightness))
                            
                            # Classic donut uses ASCII, we use gray/blue shading
                            # Let's give it a cool cyan/blue glow
                            color = (int(brightness * 0.5), brightness, brightness)
                            img.putpixel((xp, yp), color)
                
                phi += 0.04
            theta += 0.08
            
        return img
