import argparse
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

import sys
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.display_session import BleDisplaySession, UUID_WRITE


def load_payloads(path: Path) -> list[bytes]:
    payloads: list[bytes] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip().lower()
        if not line or line.startswith("#"):
            continue
        payloads.append(bytes.fromhex(line))
    return payloads


async def replay(address: str, payloads: list[bytes], interval: float, loops: int) -> None:
    async with BleDisplaySession(address=address, log_notifications=False) as session:
        loop_count = 0
        while True:
            loop_count += 1
            for index, payload in enumerate(payloads, start=1):
                await session.client.write_gatt_char(UUID_WRITE, payload, response=False)
                if interval > 0:
                    await asyncio.sleep(interval)
            print(f"Loop {loop_count} done ({len(payloads)} payloads)")
            if loops > 0 and loop_count >= loops:
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay raw fa02 payload sequence (native-scroll PoC)")
    parser.add_argument("sequence", type=Path, help="Hex payload list file (one payload per line)")
    parser.add_argument("--address", required=True, help="Panel BLE address")
    parser.add_argument("--interval", type=float, default=0.01, help="Delay between payload writes")
    parser.add_argument("--loops", type=int, default=1, help="Number of full sequence loops (0=infinite)")
    args = parser.parse_args()

    payloads = load_payloads(args.sequence)
    if not payloads:
        raise SystemExit("No payloads loaded")

    asyncio.run(replay(args.address, payloads, args.interval, args.loops))


if __name__ == "__main__":
    main()
