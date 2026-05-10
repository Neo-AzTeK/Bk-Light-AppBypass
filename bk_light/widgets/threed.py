import time
import math
import random
from PIL import Image, ImageDraw
from .base import Widget

class ThreeDWidget(Widget):
    def __init__(self, canvas_size):
        super().__init__(canvas_size)
        self.w, self.h = canvas_size
        
        self.shapes = ["cube", "torus", "pyramid", "sphere", "tesseract"]
        self.shape_queue = []
        self._refill_queue()
        self.reset_shape()

    def _refill_queue(self):
        self.shape_queue = list(self.shapes)
        random.shuffle(self.shape_queue)

    def reset_shape(self):
        if not self.shape_queue:
            self._refill_queue()
        self.current_shape = self.shape_queue.pop(0)
        self.start_time = time.time()
        self.base_color = self._random_vivid_color()
        self.rotation = [0, 0, 0]

    def _random_vivid_color(self):
        h = random.random()
        return self._hsl_to_rgb(h * 360, 1.0, 0.5)

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

    async def update(self):
        t = time.time() - self.start_time
        if t > 12:
            self.reset_shape()
        self.rotation[0] = t * 1.0
        self.rotation[1] = t * 0.6
        self.rotation[2] = t * 0.4

    def _transform(self, x, y, z):
        # Rotate X
        y, z = y*math.cos(self.rotation[0]) - z*math.sin(self.rotation[0]), y*math.sin(self.rotation[0]) + z*math.cos(self.rotation[0])
        # Rotate Y
        x, z = x*math.cos(self.rotation[1]) + z*math.sin(self.rotation[1]), -x*math.sin(self.rotation[1]) + z*math.cos(self.rotation[1])
        # Rotate Z
        x, y = x*math.cos(self.rotation[2]) - y*math.sin(self.rotation[2]), x*math.sin(self.rotation[2]) + y*math.cos(self.rotation[2])
        return x, y, z

    def _project(self, x, y, z):
        factor = 60 / (z + 50)
        px = 16 + x * factor
        py = 16 + y * factor
        return (px, py)

    def render(self) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if self.current_shape == "cube":
            self._render_wire(draw, [
                (-10,-10,-10), (10,-10,-10), (10,10,-10), (-10,10,-10),
                (-10,-10,10), (10,-10,10), (10,10,10), (-10,10,10)
            ], [
                (0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)
            ])
        elif self.current_shape == "pyramid":
            self._render_wire(draw, [
                (0,-12,0), (-10,10,-10), (10,10,-10), (10,10,10), (-10,10,10)
            ], [
                (0,1), (0,2), (0,3), (0,4), (1,2), (2,3), (3,4), (4,1)
            ])
        elif self.current_shape == "sphere":
            self._render_sphere_wire(draw)
        elif self.current_shape == "torus":
            self._render_torus_wire(draw)
        elif self.current_shape == "tesseract":
            self._render_tesseract(draw)
            
        return img

    def _render_wire(self, draw, verts, edges):
        transformed = [self._transform(*v) for v in verts]
        projected = [self._project(*v) for v in transformed]
        for start, end in edges:
            draw.line([projected[start], projected[end]], fill=self.base_color)

    def _render_sphere_wire(self, draw):
        R = 14
        # Latitude rings
        for i in range(1, 5):
            lat = math.pi * i / 5
            pts = []
            for j in range(13):
                lon = 2 * math.pi * j / 12
                x = R * math.sin(lat) * math.cos(lon)
                y = R * math.sin(lat) * math.sin(lon)
                z = R * math.cos(lat)
                pts.append(self._project(*self._transform(x, y, z)))
            draw.line(pts, fill=self.base_color)
        # Longitude rings
        for j in range(6):
            lon = math.pi * j / 6
            pts = []
            for i in range(13):
                lat = 2 * math.pi * i / 12
                x = R * math.sin(lat) * math.cos(lon)
                y = R * math.sin(lat) * math.sin(lon)
                z = R * math.cos(lat)
                pts.append(self._project(*self._transform(x, y, z)))
            draw.line(pts, fill=self.base_color)

    def _render_torus_wire(self, draw):
        R, r = 10, 5
        # Major rings
        for i in range(8):
            u = 2 * math.pi * i / 8
            pts = []
            for j in range(9):
                v = 2 * math.pi * j / 8
                x = (R + r * math.cos(v)) * math.cos(u)
                y = (R + r * math.cos(v)) * math.sin(u)
                z = r * math.sin(v)
                pts.append(self._project(*self._transform(x, y, z)))
            draw.line(pts, fill=self.base_color)
        # Minor rings
        for j in range(8):
            v = 2 * math.pi * j / 8
            pts = []
            for i in range(9):
                u = 2 * math.pi * i / 8
                x = (R + r * math.cos(v)) * math.cos(u)
                y = (R + r * math.cos(v)) * math.sin(u)
                z = r * math.sin(v)
                pts.append(self._project(*self._transform(x, y, z)))
            draw.line(pts, fill=self.base_color)

    def _render_tesseract(self, draw):
        s_in, s_out = 6, 12
        v_in = [(-s_in,-s_in,-s_in), (s_in,-s_in,-s_in), (s_in,s_in,-s_in), (-s_in,s_in,-s_in),
                (-s_in,-s_in,s_in), (s_in,-s_in,s_in), (s_in,s_in,s_in), (-s_in,s_in,s_in)]
        v_out = [(-s_out,-s_out,-s_out), (s_out,-s_out,-s_out), (s_out,s_out,-s_out), (-s_out,s_out,-s_out),
                 (-s_out,-s_out,s_out), (s_out,-s_out,s_out), (s_out,s_out,s_out), (-s_out,s_out,s_out)]
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        t_in = [self._project(*self._transform(*v)) for v in v_in]
        t_out = [self._project(*self._transform(*v)) for v in v_out]
        for s, e in edges:
            draw.line([t_in[s], t_in[e]], fill=self.base_color)
            draw.line([t_out[s], t_out[e]], fill=self.base_color)
            draw.line([t_in[s], t_out[s]], fill=(80,80,80))
