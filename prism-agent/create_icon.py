"""Generate PRISM IDS Icon file (.ico) using Pure Python Standard Library (No PIL needed)."""

import os
import struct


def create_prism_icon(filepath: str = "prism_icon.ico") -> str:
    """Generate a valid multi-size Windows .ico file using raw BMP byte encoding."""
    # 32x32 RGBA Icon (32 * 32 * 4 = 4096 bytes)
    width = 32
    height = 32
    bpp = 32

    # Create pixel buffer (Cyan Shield with Dark Slate Background)
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            # Calculate distance from center for shield shape
            dx = abs(x - 16)
            dy = abs(y - 16)
            
            # Shield boundary
            if dx <= (14 - dy // 2) and y >= 4 and y <= 28:
                if dx <= (10 - dy // 2) and y >= 8 and y <= 24:
                    # Bright Cyan Core (BGRA: 238, 211, 34, 255)
                    pixels.extend([238, 211, 34, 255])
                else:
                    # Dark Cyan Border (BGRA: 144, 116, 14, 255)
                    pixels.extend([144, 116, 14, 255])
            else:
                # Transparent Outer (BGRA: 0, 0, 0, 0)
                pixels.extend([0, 0, 0, 0])

    # BITMAPINFOHEADER (40 bytes)
    # Note: Icon height in header is doubled (height * 2 = 64) for AND mask
    header = struct.pack(
        "<IIIHHIIIIII",
        40,             # biSize
        width,          # biWidth
        height * 2,     # biHeight (doubled for ICO mask)
        1,              # biPlanes
        bpp,            # biBitCount
        0,              # biCompression (BI_RGB)
        len(pixels),    # biSizeImage
        0, 0, 0, 0      # Colors/Important
    )

    # AND Mask (1 bit per pixel, 32x32 = 128 bytes of zeros)
    and_mask = bytes(128)

    image_data = header + pixels + and_mask
    image_size = len(image_data)

    # ICONDIR (6 bytes) + 1 ICONDIRENTRY (16 bytes) = 22 bytes header offset
    icon_dir = struct.pack("<HHH", 0, 1, 1)  # Reserved, Type (1=ICO), Count (1)
    icon_entry = struct.pack(
        "<BBBBHHII",
        width,          # Width
        height,         # Height
        0,              # Color count
        0,              # Reserved
        1,              # Color planes
        bpp,            # Bits per pixel
        image_size,     # Image data size
        22              # Offset of image data
    )

    with open(filepath, "wb") as f:
        f.write(icon_dir + icon_entry + image_data)

    print(f"✅ Created pure Python ICO icon: {os.path.abspath(filepath)}")
    return filepath


if __name__ == "__main__":
    create_prism_icon()
