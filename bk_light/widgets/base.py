from abc import ABC, abstractmethod
from PIL import Image

class Widget(ABC):
    def __init__(self, canvas_size):
        self.canvas_size = canvas_size

    @abstractmethod
    async def update(self):
        """Perform background updates (e.g. API calls)."""
        pass

    @abstractmethod
    def render(self) -> Image.Image:
        """Return the current frame as a PIL Image."""
        pass
