import struct
import zlib

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

def solid_png(width: int = 1280, height: int = 720, rgb=(245, 245, 245)) -> bytes:
    r, g, b = rgb
    raw = bytearray()
    row = bytes([0, r, g, b]) * width
    for _ in range(height):
        raw.extend(row)
    comp = zlib.compress(bytes(raw), level=6)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return sig + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", comp) + _png_chunk(b"IEND", b"")
