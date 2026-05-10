import asyncio
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.config import load_config
from bk_light.panel_manager import PanelManager
from bk_light.widgets.system import SystemWidget
from bk_light.widgets.pong import PongWidget
from bk_light.widgets.fire import FireWidget
from bk_light.widgets.weather import WeatherWidget
from bk_light.widgets.github import GithubWidget
from bk_light.widgets.clock import ClockWidget
from bk_light.widgets.game_of_life import GameOfLifeWidget
from bk_light.widgets.matrix_rain import MatrixRainWidget
from bk_light.widgets.pokemon import PokemonWidget
from bk_light.widgets.nouns import NounsWidget
from bk_light.widgets.roses import RosesWidget
from bk_light.widgets.fractal import FractalWidget
from bk_light.widgets.geometry import GeometryWidget
from bk_light.widgets.threed import ThreeDWidget
from bk_light.widgets.dvd import DVDWidget
from bk_light.widgets.nyan import NyanWidget
from bk_light.widgets.bad_apple import BadAppleWidget
from bk_light.widgets.donut import DonutWidget
from bk_light.widgets.pipes import PipesWidget

WIDGET_MAP = {
    "system": SystemWidget,
    "pong": PongWidget,
    "fire": FireWidget,
    "weather": WeatherWidget,
    "github": GithubWidget,
    "clock": ClockWidget,
    "game_of_life": GameOfLifeWidget,
    "matrix_rain": MatrixRainWidget,
    "pokemon": PokemonWidget,
    "nouns": NounsWidget,
    "roses": RosesWidget,
    "fractal": FractalWidget,
    "geometry": GeometryWidget,
    "threed": ThreeDWidget,
    "dvd": DVDWidget,
    "nyan": NyanWidget,
    "bad_apple": BadAppleWidget,
    "donut": DonutWidget,
    "pipes": PipesWidget,
}

async def run_dashboard():
    config = load_config()
    
    playlist_data = config.playlist
    default_duration = config.dashboard.get("default_duration", 10.0)
    
    # Handle backwards compatibility for simple list of strings
    if playlist_data and isinstance(playlist_data[0], str):
        playlist_data = [{"widget": name, "duration": default_duration} for name in playlist_data]
    
    if not playlist_data:
        # Fallback
        playlist_data = [
            {"widget": "clock", "duration": 10},
            {"widget": "system", "duration": 10},
            {"widget": "crypto", "duration": 10},
        ]
        
    async with PanelManager(config) as manager:
        canvas_size = manager.canvas_size
        
        # Instantiate widgets
        widgets_with_duration = []
        for item in playlist_data:
            name = item.get("widget")
            duration = float(item.get("duration", default_duration))
            if name in WIDGET_MAP:
                # We instantiate one per playlist entry.
                # If a widget appears twice, it gets two separate instances
                widget_instance = WIDGET_MAP[name](canvas_size)
                widgets_with_duration.append((widget_instance, duration))
        
        if not widgets_with_duration:
            print("No valid widgets in playlist!")
            return

        print(f"Dashboard started with {len(widgets_with_duration)} widgets. Ctrl+C to stop.")
        
        current_idx = 0
        while True:
            widget, duration = widgets_with_duration[current_idx]
            print(f"Switching to {widget.__class__.__name__} for {duration}s")
            
            # Initial update safely
            try:
                await widget.update()
            except Exception as e:
                print(f"Error updating {widget.__class__.__name__}: {e}")
            
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    await widget.update()
                except Exception as e:
                    pass # Ignore mid-cycle update errors
                
                # Render and send
                try:
                    img = widget.render()
                    await manager.send_image(img, delay=0.1)
                except Exception as e:
                    print(f"Error rendering {widget.__class__.__name__}: {e}")
                
                # Frame rate of ~20fps (0.05s) to allow fluid animations like fire/pong
                await asyncio.sleep(0.05)
                
            current_idx = (current_idx + 1) % len(widgets_with_duration)

def main():
    try:
        asyncio.run(run_dashboard())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
