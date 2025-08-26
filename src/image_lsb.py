from PIL import Image
import numpy as np
import struct
from pathlib import Path

MAGIC = b"STEG1"          # 5 bytes
HEADER_FMT = ">I"          # 4-byte big-endian length

def _bytes_to_bits(data: bytes):
    for b in data:
        for i in range(8):
            yield (b >> (7 - i)) & 1

def _bits_to_bytes(bits_iter, n_bytes: int) -> bytes:
    out = bytearray()
    val = 0; count = 0
    for bit in bits_iter:
        val = (val << 1) | (bit & 1)
        count += 1
        if count == 8:
            out.append(val)
            if len(out) == n_bytes:
                return bytes(out)
            val = 0; count = 0
    raise ValueError("Not enough bits to reconstruct bytes")

def _flatten_pixels(img: Image.Image) -> np.ndarray:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    arr = np.array(img, dtype=np.uint8)
    flat = arr.reshape(-1)  # Flatten all channels
    return arr, flat

def hide(cover_path: str, payload_path: str, out_path: str):
    img = Image.open(cover_path)
    arr, flat = _flatten_pixels(img)

    payload = Path(payload_path).read_bytes()
    header = MAGIC + struct.pack(HEADER_FMT, len(payload))
    data = header + payload
    needed_bits = len(data) * 8

    if needed_bits > flat.size:
        raise ValueError(
            "Cover too small. Need {} bits, have {}.".format(needed_bits, flat.size)
        )

    # Embed: clear LSB then set with data bits
    bits = _bytes_to_bits(data)
    mod = flat.copy()
    for i, bit in zip(range(needed_bits), bits):
        mod[i] = (mod[i] & 0xFE) | bit

    # Put modified bytes back and save lossless
    stego = mod.reshape(arr.shape).astype(np.uint8)
    Image.fromarray(stego).save(out_path, format="PNG", optimize=False)
    print("Embedded {} bytes into {}".format(len(payload), out_path))

def extract(stego_path: str, out_path: str):
    img = Image.open(stego_path)
    arr, flat = _flatten_pixels(img)

    # Read header first: 5 (MAGIC) + 4 (length) = 9 bytes = 72 bits
    header_bits = (flat[i] & 1 for i in range(72))
    header = _bits_to_bytes(header_bits, 9)
    magic, length = header[:5], struct.unpack(HEADER_FMT, header[5:])[0]
    if magic != MAGIC:
        raise ValueError("Magic header not found: not a valid stego file")

    total_bits = 72 + length * 8
    if total_bits > flat.size:
        raise ValueError("Corrupted or truncated stego image (not enough bits).")

    payload_bits = (flat[i] & 1 for i in range(72, total_bits))
    payload = _bits_to_bytes(payload_bits, length)
    Path(out_path).write_bytes(payload)
    print("Extracted {} bytes to {}".format(length, out_path))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Simple PNG LSB steganography")
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hide", help="Hide payload in cover image")
    h.add_argument("cover")
    h.add_argument("payload")
    h.add_argument("out_png")

    x = sub.add_parser("extract", help="Extract payload from stego image")
    x.add_argument("stego_png")
    x.add_argument("out_file")

    args = p.parse_args()
    if args.cmd == "hide":
        hide(args.cover, args.payload, args.out_png)
    else:
        extract(args.stego_png, args.out_file)
