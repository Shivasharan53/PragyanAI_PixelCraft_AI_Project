from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter
import os
from pathlib import Path

def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except Exception: pass
    return ImageFont.load_default()

def add_text_overlay(image, text, date_text="", position="Bottom center", color="#FFFFFF", font_size=36, outline=True):
    out = image.convert("RGBA").copy()
    draw = ImageDraw.Draw(out)
    combined = "\n".join([x for x in (text.strip(), date_text.strip()) if x])
    if not combined:
        return out
    font = _font(int(font_size), True)
    bbox = draw.multiline_textbbox((0,0), combined, font=font, spacing=max(3, font_size//5), stroke_width=2 if outline else 0)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad = max(12, font_size//2)
    if "left" in position: x = pad
    elif "right" in position: x = out.width - tw - pad
    else: x = (out.width-tw)//2
    if "Top" in position: y = pad
    elif position == "Center": y = (out.height-th)//2
    else: y = out.height-th-pad
    # Subtle translucent backing helps text stay legible.
    bg = Image.new("RGBA", out.size, (0,0,0,0))
    bd = ImageDraw.Draw(bg)
    bd.rounded_rectangle((max(0,x-10), max(0,y-8), min(out.width,x+tw+10), min(out.height,y+th+8)), radius=8, fill=(0,0,0,75))
    out = Image.alpha_composite(out, bg)
    draw = ImageDraw.Draw(out)
    draw.multiline_text((x,y), combined, font=font, fill=color, spacing=max(3,font_size//5),
                        stroke_width=2 if outline else 0, stroke_fill=(0,0,0,220) if outline else None)
    return out

def _cover(image, size):
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)

def make_collage(images, filenames, title, layout="Grid", columns=3, captions=True, size=(1280,720)):
    if not images:
        raise ValueError("Upload at least one image.")
    width, height = size
    canvas = Image.new("RGB", size, (245,247,250))
    draw = ImageDraw.Draw(canvas)
    title_h = max(60, height//9) if title else 20
    if title:
        draw.rectangle((0,0,width,title_h), fill=(20,30,55))
        draw.text((width//2, title_h//2), title, anchor="mm", font=_font(max(20,height//24), True), fill="white")
    pad = max(12, width//100)
    available_h = height-title_h-pad
    if layout == "Horizontal strip":
        columns, rows = len(images), 1
    elif layout == "Vertical strip":
        columns, rows = 1, len(images)
    else:
        columns = max(1, min(int(columns), len(images)))
        rows = (len(images)+columns-1)//columns
    cell_w = (width-pad*(columns+1))//columns
    cell_h = (available_h-pad*(rows+1))//rows
    caption_h = min(42, max(22, cell_h//7)) if captions else 0
    for i, image in enumerate(images):
        row, col = divmod(i, columns)
        x, y = pad+col*(cell_w+pad), title_h+pad+row*(cell_h+pad)
        photo_h = max(1, cell_h-caption_h)
        photo = _cover(image, (cell_w, photo_h))
        canvas.paste(photo, (x,y))
        draw.rectangle((x,y,x+cell_w-1,y+photo_h-1), outline=(210,215,225), width=2)
        if captions:
            label = Path(filenames[i]).name if i < len(filenames) else f"Photo {i+1}"
            draw.text((x+6,y+photo_h+caption_h//2), label[:35], anchor="lm", font=_font(max(10, caption_h//3)), fill=(35,40,55))
    return canvas

def make_wallpaper(images, title, subtitle, size=(1920,1080), mode="Use first image"):
    if not images:
        raise ValueError("Upload at least one image.")
    if mode == "Collage all images" and len(images) > 1:
        base = make_collage(images, [f"Photo {i+1}" for i in range(len(images))], "", "Grid", 2, False, size).convert("RGBA")
    else:
        base = _cover(images[0], size).convert("RGBA")
    # Dark transparent band improves readability across bright images.
    overlay = Image.new("RGBA", size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    band_h = max(150, size[1]//3)
    d.rectangle((0, size[1]-band_h, size[0], size[1]), fill=(0,0,0,105))
    base = Image.alpha_composite(base, overlay)
    d = ImageDraw.Draw(base)
    title_font = _font(max(28,size[1]//14), True)
    sub_font = _font(max(16,size[1]//35), False)
    x = size[0]//16
    y = size[1]-band_h+size[1]//20
    d.text((x,y), title, font=title_font, fill="white", stroke_width=1, stroke_fill=(0,0,0,130))
    if subtitle:
        d.text((x,y+size[1]//10), subtitle, font=sub_font, fill=(240,244,255))
    return base
