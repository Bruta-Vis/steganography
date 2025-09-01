# Stegonography Guide

Hide a text file inside a **lossless** image (e.g., PNG) using the provided `image_lsb.py` script.

## Definitions

- Steganography is the embedding of a message in another medium.
- Least Significant Bit (LSB) steganography does this by modifying the least significant bits of pixel values to store data.

## Prerequisites
- Python 3.9+
- Install dependencies:

```bash
pip install pillow numpy
```

## Files
- `image_lsb.py` – the steganography script
- `cover.png` – your input (lossless) image
- `secret.txt` – the text you want to hide
- `stego.png` – the output image containing hidden data

## Step 1: Save Your Text to a File
```bash
echo "This is my secret message" > secret.txt
```

## Step 2: Hide the Text in the Image
```bash
python image_lsb.py hide cover.png secret.txt stego.png
```

**Arguments**
- `cover.png` → input image (use PNG or another **lossless** format)
- `secret.txt` → the file to embed
- `stego.png` → output image with embedded payload

## Step 3: Extract the Hidden Text Later
```bash
python image_lsb.py extract stego.png recovered.txt
cat recovered.txt
```

**Arguments**
- `stego.png` → image with embedded payload
- `recovered.txt` → output file for the extracted text

## Notes
- Use **lossless formats** (PNG). JPEG re-encoding will destroy simple LSB data.
- For better secrecy, **encrypt or compress** the text before embedding so the bit pattern appears random.
- The cover image must be large enough: it needs **8 bits per payload byte** plus a small header.
- The visual appearance of `stego.png` should be identical to `cover.png` to the naked eye.
