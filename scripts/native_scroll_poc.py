import argparse
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

import sys
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from bk_light.display_session import BleDisplaySession, UUID_WRITE


def load_hex_lines(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip().lower()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def build_variant(lines: list[str], variant: str) -> list[bytes]:
    # phase_anim_text_1 indexing reference from analysis (1-based):
    # 1 init control, 10/19 mid controls, 26 tail control.
    selected = list(lines)
    if variant == "no-tail" and len(selected) >= 26:
        selected = [s for i, s in enumerate(selected, start=1) if i != 26]
    elif variant == "minimal" and len(selected) >= 26:
        selected = [
            s
            for i, s in enumerate(selected, start=1)
            if i not in (10, 19, 26)
        ]
    return [bytes.fromhex(s) for s in selected]


async def run(address: str, payloads: list[bytes], interval: float, loops: int) -> None:
    async with BleDisplaySession(address=address, log_notifications=False) as session:
        loop_idx = 0
        while True:
            loop_idx += 1
            for payload in payloads:
                await session.client.write_gatt_char(UUID_WRITE, payload, response=False)
                if interval > 0:
                    await asyncio.sleep(interval)
            print(f"native-scroll-poc: loop {loop_idx} complete ({len(payloads)} payloads)")
            if loops > 0 and loop_idx >= loops:
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Native scroll PoC replay with control-packet variants")
    parser.add_argument("sequence", type=Path, help="Input sequence file (hex lines)")
    parser.add_argument("--address", required=True, help="Panel BLE address")
    parser.add_argument("--variant", choices=["full", "no-tail", "minimal"], default="no-tail")
    parser.add_argument("--interval", type=float, default=0.01)
    parser.add_argument("--loops", type=int, default=2)
    args = parser.parse_args()

    lines = load_hex_lines(args.sequence)
    payloads = build_variant(lines, args.variant)
    if not payloads:
        raise SystemExit("No payloads to replay")

    asyncio.run(run(args.address, payloads, args.interval, args.loops))


if __name__ == "__main__":
    main()
