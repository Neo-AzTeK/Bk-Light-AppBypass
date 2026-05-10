# Developer Guide: Adding New Widgets

This project is designed to be modular. To add a new widget to your 32x32 LED dashboard, follow this architectural roadmap.

---

## 1. Core Architecture
All widgets are located in `bk_light/widgets/`.

### The Base Class: `bk_light/widgets/base.py`
Every widget **must** inherit from the `Widget` class.
- `__init__(self, canvas_size)`: Receives `(32, 32)`. Use this to load fonts, presets, or initialize state.
- `async update(self)`: Use this for logic (physics, API calls, state changes). It's async to allow non-blocking network requests.
- `render(self) -> Image.Image`: Must return a `PIL.Image` of size `(32, 32)` in `RGB` mode.

---

## 2. Configuration & Presets
We use a two-tier configuration system.

### `presets.yaml`
Add a section here for your widget's visual or behavioral settings (colors, speeds, target URLs). 
```yaml
  my_new_widget:
    default:
      speed: 1.0
      color: [255, 0, 0]
```

### `bk_light/config.py`
To make your preset accessible in Python:
1.  Add a `@dataclass` for your preset (e.g., `MyWidgetPreset`).
2.  Add it to the `PresetLibrary` dataclass.
3.  Update the `load_presets` function to parse your new section.

---

## 3. Registration Checklist
Once your `.py` file is created in `bk_light/widgets/`, you need to register it in two places:

1.  **`scripts/dashboard.py`**:
    - Import your class.
    - Add it to the `WIDGET_MAP` dictionary.
2.  **`playlist.yaml`**:
    - Add the widget name and its desired duration to the list.

---

## 4. Helper Utilities
- **Text Rendering**: Use `bk_light.text.build_text_bitmap` for pixel-perfect text.
- **Fonts**: Use `bk_light.fonts.resolve_font("ipixel")` to get the standard 8pt pixel font.
- **Panel Control**: The `PanelManager` in `bk_light/panel_manager.py` handles the BLE communication (usually you don't need to touch this).

---

## 5. Testing Your Widget
Use the preview tool to test your widget in isolation without running the full dashboard rotation:
```powershell
uv run preview <your_widget_name>
```
