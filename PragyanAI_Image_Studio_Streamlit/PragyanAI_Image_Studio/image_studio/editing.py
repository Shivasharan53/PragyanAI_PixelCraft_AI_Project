from PIL import Image, ImageEnhance, ImageOps, ImageFilter, ImageChops
from io import BytesIO
import cv2
import numpy as np

def enhance_image(image, brightness=1, contrast=1, color=1, sharpness=1):
    out = ImageEnhance.Brightness(image).enhance(brightness)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    out = ImageEnhance.Color(out).enhance(color)
    return ImageEnhance.Sharpness(out).enhance(sharpness)

def _fit_overlay(overlay, size, fit):
    if fit == "Stretch to base":
        return overlay.resize(size, Image.Resampling.LANCZOS)
    if fit == "Contain":
        return ImageOps.pad(overlay, size, method=Image.Resampling.LANCZOS, color=(0,0,0,0))
    return ImageOps.fit(overlay, size, method=Image.Resampling.LANCZOS)

def blend_images(base, overlay, opacity=0.5, mode="Normal", fit="Cover/crop to base"):
    base = base.convert("RGBA")
    overlay = _fit_overlay(overlay.convert("RGBA"), base.size, fit)
    alpha = overlay.getchannel("A").point(lambda p: int(p * opacity))
    overlay.putalpha(alpha)
    if mode == "Normal":
        return Image.alpha_composite(base, overlay)
    a = np.asarray(base.convert("RGB")).astype(np.float32) / 255
    b = np.asarray(overlay.convert("RGB")).astype(np.float32) / 255
    if mode == "Multiply":
        mixed = a * b
    elif mode == "Screen":
        mixed = 1 - (1-a)*(1-b)
    else:
        mixed = np.clip(a+b, 0, 1)
    mixed = (mixed * 255).astype(np.uint8)
    blend = Image.fromarray(mixed, "RGB").convert("RGBA")
    return Image.blend(base, blend, opacity)

def grayscale_image(image, contrast=1.0):
    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    return gray.convert("RGB")

def sketch_image(image, style="Pencil", strength=9):
    rgb = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    k = max(3, int(strength) | 1)
    if style == "Bold line art":
        smooth = cv2.medianBlur(gray, k)
        edges = cv2.adaptiveThreshold(smooth, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, max(3, k*2+1), 7)
        return Image.fromarray(cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB))
    inverted = 255 - gray
    blur = cv2.GaussianBlur(inverted, (k, k), 0)
    denom = np.maximum(1, 255 - blur)
    dodge = np.clip(gray.astype(np.float32) * 255 / denom, 0, 255).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(dodge, cv2.COLOR_GRAY2RGB))

def replace_background(subject, background, fit="Cover/crop"):
    try:
        from rembg import remove
    except Exception as exc:
        raise RuntimeError("Background removal requires rembg. Install dependencies with `pip install -r requirements.txt` and restart the app. Original error: " + str(exc))
    source = BytesIO()
    subject.convert("RGBA").save(source, format="PNG")
    cutout_bytes = remove(source.getvalue())
    cutout = Image.open(BytesIO(cutout_bytes)).convert("RGBA")
    bg = background.convert("RGBA")
    if fit == "Stretch":
        bg = bg.resize(cutout.size, Image.Resampling.LANCZOS)
    else:
        bg = ImageOps.fit(bg, cutout.size, method=Image.Resampling.LANCZOS)
    # Keep a soft edge for a more natural composite.
    alpha = cutout.getchannel("A").filter(ImageFilter.GaussianBlur(0.4))
    cutout.putalpha(alpha)
    bg.alpha_composite(cutout)
    return bg
