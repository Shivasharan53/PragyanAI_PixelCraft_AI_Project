"""Image loading, conversion, and download utilities."""

from io import BytesIO
from pathlib import Path
import re

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_IMAGE_PIXELS = 40_000_000


def load_image(uploaded_file):
    """Load an uploaded image safely and correct its orientation."""
    if uploaded_file is None:
        return None

    try:
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as source:
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError(
                    "This image is too large. Please upload an image "
                    "with fewer than 40 million pixels."
                )

            source.load()
            image = ImageOps.exif_transpose(source)
            return image.copy()

    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            "This file is not a supported image or the image is damaged."
        ) from exc


def image_to_bytes(image, image_format="PNG", quality=95):
    """Convert a PIL image into downloadable bytes."""
    output = BytesIO()
    fmt = image_format.upper()

    if fmt in ("JPG", "JPEG"):
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            rgb = Image.new("RGB", rgba.size, "white")
            rgb.paste(rgba, mask=rgba.getchannel("A"))
            image = rgb
        else:
            image = image.convert("RGB")

        image.save(
            output,
            format="JPEG",
            quality=max(1, min(100, int(quality))),
            optimize=True,
        )
    elif fmt == "WEBP":
        image.save(
            output,
            format="WEBP",
            quality=max(1, min(100, int(quality))),
        )
    else:
        image.save(output, format="PNG", optimize=True)

    return output.getvalue()


def safe_filename(filename, default="edited_image"):
    """Remove unsafe characters from a filename."""
    name = Path(filename or default).stem
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
    return (name or default)[:100]
