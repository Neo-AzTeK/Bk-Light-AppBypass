import asyncio
import re
from pathlib import Path
from bleak import BleakScanner

CONFIG_PATH = Path("config.yaml")

async def scan_devices():
    print("Scanning for BK-Light compatible devices (starting with 'LED_BLE')...")
    devices = await BleakScanner.discover(timeout=5.0)
    # Filter for devices that look like our panels
    compatible = [d for d in devices if d.name and (d.name.startswith("LED_BLE") or "BK-Light" in d.name)]
    return compatible

def update_config_address(address: str):
    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} not found. Please ensure you are in the project root.")
        return False
    
    content = CONFIG_PATH.read_text(encoding="utf-8")
    # Simple regex to replace the address field while keeping the rest
    new_content = re.sub(r'address:.*', f'address: "{address}"', content)
    
    if new_content == content and 'address:' not in content:
        # If the key doesn't exist, append it to the device section
        if 'device:' in content:
            new_content = content.replace('device:', f'device:\n  address: "{address}"')
        else:
            new_content = f"device:\n  address: \"{address}\"\n" + content
            
    CONFIG_PATH.write_text(new_content, encoding="utf-8")
    return True

async def main():
    devices = await scan_devices()
    
    if not devices:
        print("No compatible devices found. Make sure your panel is powered on and in range.")
        return

    print("\nFound compatible devices:")
    for i, dev in enumerate(devices):
        print(f"[{i+1}] {dev.name} ({dev.address})")

    try:
        choice = input(f"\nSelect a device (1-{len(devices)}) or 'q' to quit: ")
        if choice.lower() == 'q':
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(devices):
            selected = devices[idx]
            print(f"Updating config with address: {selected.address}")
            if update_config_address(selected.address):
                print("Successfully updated config.yaml!")
            else:
                print("Failed to update config.yaml.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")

if __name__ == "__main__":
    asyncio.run(main())
