#!/usr/bin/env python3
import argparse
import asyncio
import sys
import zlib
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from bk_light.display_session import BleDisplaySession, UUID_WRITE
from scripts.ipixel_font_map import glyph_8x10_ipixel, validate_known_glyphs


BASE_PAYLOAD = bytes.fromhex(
    "45000001003600000000000000000202000101015000ffffff0000000000ffffff000000"
    "0000000000000000000000000000ffffff00000000000000000000000000000000"
)


def build_content_payload(text2: str, channel: int) -> bytes:
    text2 = (text2 or "  ")[:2].ljust(2)
    p = bytearray(BASE_PAYLOAD)
    p[14] = channel & 0xFF

    g1 = glyph_8x10_ipixel(text2[0])
    g2 = glyph_8x10_ipixel(text2[1])
    p[36:46] = g1
    p[56:66] = g2

    crc = zlib.crc32(bytes(p[15:])) & 0xFFFFFFFF
    p[9:13] = crc.to_bytes(4, "little")
    return bytes(p)


def build_handshake() -> bytes:
    now = datetime.now()
    return bytes((0x08, 0x00, 0x01, 0x80, now.hour & 0xFF, now.minute & 0xFF, now.second & 0xFF, 0x00))


async def run(address: str, text: str, channel: int, interval: float, verbose: bool):
    payload5 = build_content_payload(text, channel)
    seq = [
        build_handshake(),
        bytes.fromhex("04000580"),
        bytes.fromhex("0500128007"),
        bytes.fromhex(f"070008800100{channel:02x}"),
        payload5,
    ]

    if verbose:
        print("payload5", payload5.hex())

    async with BleDisplaySession(address=address, log_notifications=verbose) as s:
        for i, pkt in enumerate(seq, 1):
            await s.client.write_gatt_char(UUID_WRITE, pkt, response=False)
            await asyncio.sleep(interval)
            if verbose:
                print("sent", i)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Send native 5-packet text-scroll payload (2-char prototype)")
    ap.add_argument("text", help="Text to display (currently first 2 chars used)")
    ap.add_argument("--address", default="31:C3:BD:32:14:7A")
    ap.add_argument("--channel", type=int, default=3)
    ap.add_argument("--interval", type=float, default=0.06)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument(
        "--validate-font",
        action="store_true",
        help="Validate recovered native glyphs against known A/B captures and exit",
    )
    args = ap.parse_args()

    if args.validate_font:
        results = validate_known_glyphs()
        for ch, ok in sorted(results.items()):
            print(f"{ch}: {'ok' if ok else 'mismatch'}")
        raise SystemExit(0 if all(results.values()) else 1)

    asyncio.run(run(args.address, args.text, args.channel, args.interval, args.verbose))
