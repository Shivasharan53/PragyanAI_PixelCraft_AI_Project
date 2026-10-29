from PIL import Image, ImageDraw
from .design import _font
from io import BytesIO

def add_geotag_overlay(image, place, latitude="", longitude="", date_text=""):
    lines = [x.strip() for x in [place, f"{latitude}, {longitude}" if latitude.strip() and longitude.strip() else "", date_text] if x.strip()]
    text = "\n".join(lines)
    out = image.convert("RGBA").copy()
    font_size = max(14, out.width//45)
    font = _font(font_size, True)
    draw = ImageDraw.Draw(out)
    box = draw.multiline_textbbox((0,0), text, font=font, spacing=4)
    tw, th = box[2]-box[0], box[3]-box[1]
    pad = max(10, out.width//100)
    x, y = pad, out.height-th-pad
    draw.rounded_rectangle((x-pad,y-pad,x+tw+pad,y+th+pad), radius=8, fill=(0,0,0,150))
    draw.multiline_text((x,y), text, font=font, fill="white", spacing=4)
    return out

def _dms(value):
    value = abs(float(value))
    degrees = int(value)
    minutes_full = (value - degrees) * 60
    minutes = int(minutes_full)
    seconds = round((minutes_full - minutes) * 60 * 10000)
    return ((degrees,1),(minutes,1),(seconds,10000))

def embed_gps_metadata(image, latitude, longitude):
    try:
        import piexif
    except Exception as exc:
        raise RuntimeError("Install piexif to embed GPS EXIF metadata: pip install piexif") from exc
    lat, lon = float(latitude), float(longitude)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Latitude must be between -90 and 90 and longitude between -180 and 180.")
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    gps = exif_dict["GPS"]
    gps[piexif.GPSIFD.GPSLatitudeRef] = b"N" if lat >= 0 else b"S"
    gps[piexif.GPSIFD.GPSLatitude] = _dms(lat)
    gps[piexif.GPSIFD.GPSLongitudeRef] = b"E" if lon >= 0 else b"W"
    gps[piexif.GPSIFD.GPSLongitude] = _dms(lon)
    exif_bytes = piexif.dump(exif_dict)
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=95, exif=exif_bytes)
    return buffer.getvalue()
