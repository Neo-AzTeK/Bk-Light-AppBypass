import argparse
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.config import load_config
from bk_light.panel_manager import PanelManager
from scripts.dashboard import WIDGET_MAP

async def run_preview(widget_name: str):
    if widget_name not in WIDGET_MAP:
        print(f"\nError: Unknown widget '{widget_name}'")
        print(f"Available widgets: {', '.join(sorted(WIDGET_MAP.keys()))}")
        return

    config = load_config()
    WidgetClass = WIDGET_MAP[widget_name]

    print(f"\nPreviewing '{widget_name}' widget...")
    print("Press Ctrl+C to stop the preview.")

    try:
        async with PanelManager(config) as manager:
            widget = WidgetClass(manager.canvas_size)
            
            # Initial update
            try:
                await widget.update()
            except Exception as e:
                print(f"Initial update warning: {e}")

            while True:
                try:
                    await widget.update()
                except Exception as e:
                    pass

                try:
                    img = widget.render()
                    await manager.send_image(img, delay=0.05)
                except Exception as e:
                    print(f"Render error: {e}")

                await asyncio.sleep(0.05)
    except Exception as e:
        print(f"\nConnection error: {e}")

def main():
    # Sort for consistent display
    available = ", ".join(sorted(WIDGET_MAP.keys()))
    
    # Custom help if no arguments provided
    if len(sys.argv) == 1:
        print("Usage: uv run preview [-h|--help] <widget>")
        print(f"Available widgets: {available}")
        sys.exit(0)
    
    parser = argparse.ArgumentParser(
        description="Preview a single dashboard widget on your LED panel.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "widget", 
        metavar="<widget>",
        help=f"Name of the widget to preview.\nAvailable: {available}"
    )
    
    args = parser.parse_args()

    try:
        asyncio.run(run_preview(args.widget.lower()))
    except KeyboardInterrupt:
        print("\nPreview stopped.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nUnhandled error: {e}")

if __name__ == "__main__":
    main()
