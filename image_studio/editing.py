"""Image enhancement, blending, effects, and AI background replacement."""

from functools import lru_cache
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def enhance_image(
    image,
    brightness=1.0,
    contrast=1.0,
    color=1.0,
    sharpness=1.0,
):
    """Adjust brightness, contrast, color, and sharpness."""
    result = image.convert("RGB")
    result = ImageEnhance.Brightness(result).enhance(float(brightness))
    result = ImageEnhance.Contrast(result).enhance(float(contrast))
    result = ImageEnhance.Color(result).enhance(float(color))
    result = ImageEnhance.Sharpness(result).enhance(float(sharpness))
    return result


def _fit_overlay(overlay, size, fit):
    """Resize an overlay to match the base image."""
    if fit in ("Stretch", "Stretch to base"):
        return overlay.resize(size, Image.Resampling.LANCZOS)

    if fit == "Contain":
        return ImageOps.pad(
            overlay,
            size,
            method=Image.Resampling.LANCZOS,
            color=(0, 0, 0, 0),
        )

    return ImageOps.fit(
        overlay,
        size,
        method=Image.Resampling.LANCZOS,
    )


def blend_images(
    base,
    overlay,
    opacity=0.5,
    mode="Normal",
    fit="Cover/crop to base",
):
    """Blend two images using common compositing modes."""
    opacity = max(0.0, min(1.0, float(opacity)))

    base_rgba = base.convert("RGBA")
    overlay_rgba = _fit_overlay(overlay.convert("RGBA"), base_rgba.size, fit)

    if mode == "Normal":
        overlay_rgba.putalpha(
            overlay_rgba.getchannel("A").point(
                lambda value: round(value * opacity)
            )
        )
        return Image.alpha_composite(base_rgba, overlay_rgba)

    first = np.asarray(base_rgba.convert("RGB"), dtype=np.float32) / 255.0
    second = np.asarray(overlay_rgba.convert("RGB"), dtype=np.float32) / 255.0

    if mode == "Multiply":
        mixed = first * second
    elif mode == "Screen":
        mixed = 1.0 - (1.0 - first) * (1.0 - second)
    elif mode == "Add":
        mixed = np.clip(first + second, 0.0, 1.0)
    else:
        raise ValueError(f"Unsupported blend mode: {mode}")

    mixed_image = Image.fromarray(
        np.uint8(np.clip(mixed * 255.0, 0, 255))
    ).convert("RGBA")

    return Image.blend(base_rgba, mixed_image, opacity)


def grayscale_image(image, contrast=1.0, brightness=1.0):
    """Convert an image to black and white with optional adjustments."""
    result = ImageOps.grayscale(image.convert("RGB"))
    result = ImageEnhance.Brightness(result).enhance(float(brightness))
    result = ImageEnhance.Contrast(result).enhance(float(contrast))
    return result.convert("RGB")


def sketch_image(image, style="Pencil", strength=9):
    """Create pencil, charcoal, or line-art effects."""
    rgb = np.asarray(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    strength = max(3, min(31, int(strength)))
    if strength % 2 == 0:
        strength += 1

    if style == "Bold line art":
        smooth = cv2.medianBlur(gray, strength)
        block_size = min(51, strength * 2 + 1)
        if block_size % 2 == 0:
            block_size += 1

        edges = cv2.adaptiveThreshold(
            smooth,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            block_size,
            7,
        )
        return Image.fromarray(edges).convert("RGB")

    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (strength, strength), 0)
    denominator = np.maximum(1, 255 - blurred)

    sketch = np.clip(
        gray.astype(np.float32) * 255.0 / denominator,
        0,
        255,
    ).astype(np.uint8)

    if style == "Charcoal":
        sketch = cv2.convertScaleAbs(sketch, alpha=1.35, beta=-20)
        sketch = cv2.GaussianBlur(sketch, (3, 3), 0)

    return Image.fromarray(sketch).convert("RGB")


@lru_cache(maxsize=1)
def _get_background_session():
    """Load a smaller rembg model once per running app process."""
    try:
        from rembg import new_session
    except Exception as exc:
        raise RuntimeError(
            "Background removal dependencies could not be loaded. "
            "Check requirements.txt and redeploy the app. "
            f"Technical detail: {exc}"
        ) from exc

    try:
        # u2netp is substantially smaller than the default BRIA model.
        return new_session("u2netp")
    except Exception as exc:
        raise RuntimeError(
            "The AI background-removal model could not be initialized. "
            "Check the Streamlit Cloud logs and available memory. "
            f"Technical detail: {exc}"
        ) from exc


def remove_image_background(image):
    """Return the subject with a transparent background."""
    try:
        from rembg import remove
    except Exception as exc:
        raise RuntimeError(
            "The rembg package is unavailable. Check requirements.txt "
            f"and redeploy. Technical detail: {exc}"
        ) from exc

    try:
        source = BytesIO()
        image.convert("RGBA").save(source, format="PNG")

        output = remove(
            source.getvalue(),
            session=_get_background_session(),
        )

        result = Image.open(BytesIO(output)).convert("RGBA")
        result.load()

        if result.width == 0 or result.height == 0:
            raise ValueError("The AI model returned an empty image.")

        return result

    except Exception as exc:
        if isinstance(exc, RuntimeError):
            raise

        raise RuntimeError(
            "AI background removal failed while processing this image. "
            "Try a smaller JPG or PNG with the subject clearly visible. "
            f"Technical detail: {exc}"
        ) from exc


def replace_background(subject, background, fit="Cover/crop"):
    """Remove the subject's old background and place it over a new one."""
    cutout = remove_image_background(subject).convert("RGBA")
    background = background.convert("RGBA")

    if fit == "Stretch":
        background = background.resize(
            cutout.size,
            Image.Resampling.LANCZOS,
        )
    else:
        background = ImageOps.fit(
            background,
            cutout.size,
            method=Image.Resampling.LANCZOS,
        )

    # A very small blur softens jagged mask edges without removing detail.
    alpha = cutout.getchannel("A").filter(ImageFilter.GaussianBlur(0.4))
    cutout.putalpha(alpha)

    background.alpha_composite(cutout)
    return background
