import argparse
import re
from pathlib import Path


def parse_btmon_text(path: Path) -> list[str]:
    lines = path.read_text(errors="ignore").splitlines()
    payloads: list[str] = []
    for i, line in enumerate(lines):
        if "ATT: Write Command (0x52)" not in line:
            continue
        is_fa02 = False
        payload = None
        for j in range(i + 1, min(i + 8, len(lines))):
            probe = lines[j]
            if "Type: Unknown (0xfa02)" in probe:
                is_fa02 = True
            m = re.search(r"Data\[\d+\]:\s*([0-9a-fA-F ]+)", probe)
            if m:
                payload = m.group(1).replace(" ", "").lower()
                break
        if is_fa02 and payload:
            payloads.append(payload)
    return payloads


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract fa02 write payloads from btmon text log")
    parser.add_argument("btmon_text", type=Path, help="Path to btmon-decoded text file")
    parser.add_argument("--out", type=Path, default=Path("tmp/fa02_sequence.txt"), help="Output hex list file")
    args = parser.parse_args()

    payloads = parse_btmon_text(args.btmon_text)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(payloads) + "\n", encoding="utf-8")
    print(f"Wrote {len(payloads)} payloads -> {args.out}")


if __name__ == "__main__":
    main()
