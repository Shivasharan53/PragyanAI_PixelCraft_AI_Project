from io import BytesIO
import re
from PIL import Image, ImageOps, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = False

def load_image(data):
    image = Image.open(BytesIO(data))
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    return image.copy()

def image_to_bytes(image, fmt="PNG"):
    buffer = BytesIO()
    if fmt.upper() in ("JPG", "JPEG"):
        image.convert("RGB").save(buffer, format="JPEG", quality=95, optimize=True)
    else:
        image.save(buffer, format=fmt.upper(), optimize=True)
    return buffer.getvalue()

def safe_filename(name):
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("._")
    return (name or "image")[:100]
