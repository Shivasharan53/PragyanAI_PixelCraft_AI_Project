
from io import BytesIO

import cv2
import numpy as np
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps,
)


# --------------------------------------------------
# 1. IMAGE ENHANCEMENT
# --------------------------------------------------

def enhance_image(
    image,
    brightness=1.0,
    contrast=1.0,
    color=1.0,
    sharpness=1.0,
):
    """Adjust brightness, contrast, color, and sharpness."""
    result = image.convert("RGB")

    result = ImageEnhance.Brightness(result).enhance(
        float(brightness)
    )
    result = ImageEnhance.Contrast(result).enhance(
        float(contrast)
    )
    result = ImageEnhance.Color(result).enhance(
        float(color)
    )
    result = ImageEnhance.Sharpness(result).enhance(
        float(sharpness)
    )

    return result


# --------------------------------------------------
# 2. OVERLAY SIZE AND FITTING
# --------------------------------------------------

def _fit_overlay(overlay, size, fit):
    """Resize or crop an overlay to match the base image."""
    overlay = overlay.convert("RGBA")

    if fit == "Stretch to base":
        return overlay.resize(
            size, Image.Resampling.LANCZOS
        )

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


# --------------------------------------------------
# 3. IMAGE BLENDING
# --------------------------------------------------

def blend_images(
    base,
    overlay,
    opacity=0.5,
    mode="Normal",
    fit="Cover/crop to base",
):
    """Blend two images using several blend modes."""
    base = base.convert("RGBA")
    opacity = max(0.0, min(1.0, float(opacity)))

    overlay = _fit_overlay(
        overlay, base.size, fit
    )

    if mode == "Normal":
        overlay_alpha = overlay.getchannel("A").point(
            lambda value: round(value * opacity)
        )
        overlay.putalpha(overlay_alpha)
        return Image.alpha_composite(base, overlay)

    base_array = (
        np.asarray(base.convert("RGB")).astype(np.float32)
        / 255.0
    )
    overlay_array = (
        np.asarray(overlay.convert("RGB")).astype(np.float32)
        / 255.0
    )

    if mode == "Multiply":
        mixed = base_array * overlay_array

    elif mode == "Screen":
        mixed = 1.0 - (
            (1.0 - base_array) * (1.0 - overlay_array)
        )

    elif mode == "Add":
        mixed = np.clip(
            base_array + overlay_array, 0.0, 1.0
        )

    else:
        mixed = overlay_array

    mixed_image = Image.fromarray(
        np.clip(mixed * 255, 0, 255).astype(np.uint8),
        mode="RGB",
    ).convert("RGBA")

    # Respect overlay transparency when blending.
    overlay_mask = (
        np.asarray(overlay.getchannel("A")).astype(np.float32)
        / 255.0
    ) * opacity

    base_rgba = np.asarray(base).astype(np.float32)
    mixed_rgba = np.asarray(mixed_image).astype(np.float32)

    effective_alpha = (
        overlay_mask[..., None]
    )

    output = base_rgba.copy()
    output[..., :3] = (
        base_rgba[..., :3] * (1.0 - effective_alpha)
        + mixed_rgba[..., :3] * effective_alpha
    )

    return Image.fromarray(
        np.clip(output, 0, 255).astype(np.uint8),
        mode="RGBA",
    )


# --------------------------------------------------
# 4. BLACK AND WHITE / GRAYSCALE
# --------------------------------------------------

def grayscale_image(image, contrast=1.0):
    """Convert an image to black and white."""
    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(
        float(contrast)
    )

    return gray.convert("RGB")


# --------------------------------------------------
# 5. COLOR PHOTO TO SKETCH
# --------------------------------------------------

def sketch_image(image, style="Pencil", strength=9):
    """Create a pencil sketch or bold line-art effect."""
    rgb = np.asarray(
        image.convert("RGB")
    )

    gray = cv2.cvtColor(
        rgb, cv2.COLOR_RGB2GRAY
    )

    # Ensure the kernel size is an odd number >= 3.
    kernel_size = max(3, int(strength))
    if kernel_size % 2 == 0:
        kernel_size += 1

    if style == "Bold line art":
        # Median blur kernel must fit the image dimensions.
        max_kernel = min(gray.shape[:2])
        if max_kernel % 2 == 0:
            max_kernel -= 1

        kernel_size = min(kernel_size, max(3, max_kernel))

        smooth = cv2.medianBlur(
            gray, kernel_size
        )

        threshold_size = min(
            kernel_size * 2 + 1,
            min(gray.shape[:2])
            if min(gray.shape[:2]) % 2 == 1
            else min(gray.shape[:2]) - 1,
        )
        threshold_size = max(3, threshold_size)

        edges = cv2.adaptiveThreshold(
            smooth,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            threshold_size,
            7,
        )

        return Image.fromarray(
            cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        )

    inverted = 255 - gray

    blurred = cv2.GaussianBlur(
        inverted,
        (kernel_size, kernel_size),
        0,
    )

    denominator = np.maximum(
        1, 255 - blurred
    )

    pencil = np.clip(
        gray.astype(np.float32) * 255.0 / denominator,
        0,
        255,
    ).astype(np.uint8)

    return Image.fromarray(
        cv2.cvtColor(pencil, cv2.COLOR_GRAY2RGB)
    )


# --------------------------------------------------
# 6. REMOVE IMAGE BACKGROUND
# --------------------------------------------------

def remove_image_background(subject):
    """
    Remove the background and return a transparent RGBA image.

    The rembg package and its AI model are loaded only
    when this function is called.
    """
    try:
        from rembg import remove
    except Exception as exc:
        raise RuntimeError(
            "Background removal could not load rembg. "
            "Check your requirements.txt and Python version. "
            f"Details: {exc}"
        ) from exc

    source = BytesIO()
    subject.convert("RGBA").save(
        source, format="PNG"
    )

    try:
        cutout_bytes = remove(
            source.getvalue()
        )

        result = Image.open(
            BytesIO(cutout_bytes)
        ).convert("RGBA")

        return result

    except Exception as exc:
        raise RuntimeError(
            "The AI background-removal process failed. "
            "The model may be unavailable or the server "
            "may have insufficient memory. "
            f"Details: {exc}"
        ) from exc


# --------------------------------------------------
# 7. REPLACE BACKGROUND WITH ANOTHER IMAGE
# --------------------------------------------------

def replace_background(
    subject,
    background,
    fit="Cover/crop",
):
    """
    Remove the subject's original background and place
    the subject onto a replacement background image.
    """
    cutout = remove_image_background(subject)

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

    # Slightly soften the subject's alpha edges.
    alpha = cutout.getchannel("A").filter(
        ImageFilter.GaussianBlur(0.4)
    )
    cutout.putalpha(alpha)

    background.alpha_composite(cutout)

    return background
