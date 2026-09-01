#!/usr/bin/env python3
"""Analyze the Shannon entropy of a file.

The analyzer streams the file in chunks, calculates the byte-frequency
distribution, and reports entropy in bits per byte. High entropy can be
consistent with compression, encryption, or packed data, but entropy alone
cannot determine which one is present.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path


DEFAULT_CHUNK_SIZE = 1024 * 1024
HIGH_ENTROPY_THRESHOLD = 7.5
LOW_ENTROPY_THRESHOLD = 3.0


def shannon_entropy_from_counts(counts: collections.Counter[int], total: int) -> float:
    """Calculate Shannon entropy from byte counts."""
    if total <= 0:
        return 0.0

    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
        if count
    )


def analyze_file(
    path: Path,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> tuple[int, float]:
    """Read a file incrementally and return (size, Shannon entropy)."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    counts: collections.Counter[int] = collections.Counter()
    total = 0

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            counts.update(chunk)
            total += len(chunk)

    return total, shannon_entropy_from_counts(counts, total)


def classify_entropy(entropy: float) -> str:
    """Return a conservative interpretation of an entropy score."""
    if entropy > HIGH_ENTROPY_THRESHOLD:
        return "High entropy; consistent with compressed, encrypted, or packed data."
    if entropy < LOW_ENTROPY_THRESHOLD:
        return "Low entropy; consistent with plain text or repetitive data."
    return "Moderate entropy; no strong classification from entropy alone."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate Shannon entropy for a file."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="path to the file to analyze",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="read size in bytes (default: 1048576)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="output format (default: text)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.chunk_size <= 0:
        parser.error("--chunk-size must be greater than zero")

    path = Path(args.file).expanduser()

    try:
        size, entropy = analyze_file(path, chunk_size=args.chunk_size)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    except PermissionError:
        print(f"ERROR: permission denied: {path}", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"ERROR: expected a file, got a directory: {path}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: unable to read {path}: {exc}", file=sys.stderr)
        return 1

    interpretation = classify_entropy(entropy)

    if args.output_format == "json":
        payload = {
            "file": str(path.resolve(strict=False)),
            "size_bytes": size,
            "shannon_entropy_bits_per_byte": round(entropy, 6),
            "maximum_entropy_bits_per_byte": 8.0,
            "interpretation": interpretation,
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"File: {path}")
    print(f"File size: {size:,} bytes")
    print(f"Shannon entropy: {entropy:.3f} bits/byte (maximum 8.0)")
    print(f"Assessment: {interpretation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
