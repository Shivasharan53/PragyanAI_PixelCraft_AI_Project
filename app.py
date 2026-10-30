import io
import math
from datetime import date
import numpy as np
import cv2
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Studio · Creative Image Suite",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# TOOL CATALOG & CATEGORIES
# ---------------------------------------------------------
CATEGORIES = {
    "⚡ Quick Adjustments": [
        ("Image Enhancement", "Fine-tune brightness, contrast, saturation, and sharpness."),
        ("Black & White", "Convert photos to monochrome with fine contrast controls."),
        ("File Size Compressor", "Compress images to meet strict KB/MB upload limits."),
    ],
    "🎨 Creative Effects": [
        ("Color Splash", "Keep a single vibrant hue while turning the rest into black & white."),
        ("Color to Sketch", "Convert photos into pencil-style line art."),
        ("Image Blending", "Composite two images using opacity and blending modes."),
        ("AI Background Change", "Segment subjects and replace backgrounds with colors or images."),
    ],
    "🖨 Utility & Print": [
        ("Passport Photo Sheet", "Tile 35x45mm passport photos onto A4 or Letter sheets."),
        ("Stamp Photo Maker", "Generate printable sheets of compact stamp-sized photos."),
        ("Image Geotagging", "Stamp visible location names, GPS coordinates, and dates."),
        ("Add Date & Text", "Overlay custom typography, captions, and watermarks."),
    ],
    "📐 Layouts & Comparisons": [
        ("Collage Maker", "Combine multiple photos into customizable grid collages."),
        ("Wallpaper Designer", "Generate phone, desktop, or square wallpapers with typography."),
        ("Image Similarity", "Calculate pixel-level difference and similarity scores."),
    ],
}

# ---------------------------------------------------------
# MODERN DESIGN SYSTEM (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

:root {
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --bg-page: #f8fafc;
    --card-bg: #ffffff;
    --border-color: #e2e8f0;
}

.stApp {
    background: var(--bg-page);
    color: #0f172a;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid #1e293b !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
    color: #94a3b8 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #cbd5e1 !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    text-align: left !important;
    padding: 0.45rem 0.75rem !important;
    transition: all 0.15s ease-in-out !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e293b !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35) !important;
}

/* Studio Hero Header */
.studio-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03);
}
.studio-badge {
    display: inline-block;
    padding: 4px 10px;
    background: #ede9fe;
    color: #6366f1;
    font-size: 0.75rem;
    font-weight: 700;
    border-radius: 9999px;
    margin-bottom: 8px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.studio-hero h1 {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 6px 0;
    letter-spacing: -0.025em;
}
.studio-hero p {
    color: #64748b;
    margin: 0;
    font-size: 0.95rem;
}

/* Container Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 14px !important;
    padding: 1.25rem !important;
    box-shadow: 0 2px 8px -1px rgba(0, 0, 0, 0.04) !important;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 12px rgba(99, 102, 241, 0.25) !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35) !important;
}

/* Tabs & Preview Frame */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 6px 14px; font-weight: 600; }
div[data-testid="stImage"] img { border-radius: 10px; border: 1px solid var(--border-color); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "Image Enhancement"

if "result_image" not in st.session_state:
    st.session_state.result_image = None

if "result_name" not in st.session_state:
    st.session_state.result_name = "studio-edit.png"

# ---------------------------------------------------------
# IMAGE HELPERS
# ---------------------------------------------------------
def load_image(upload):
    if upload is None:
        return None
    try:
        image = Image.open(upload)
        image.load()
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception:
        st.error("Could not load image. Please provide a valid JPG, PNG, or WEBP file.")
        return None

def png_bytes(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

def fit_image(image, size):
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)

def make_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()

def save_result(image, filename="studio-output.png"):
    st.session_state.result_image = image.copy()
    st.session_state.result_name = filename

def add_text_overlay(image, text, position, color, size):
    out = image.convert("RGBA").copy()
    draw = ImageDraw.Draw(out)
    font = make_font(size)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = max(8, (out.width - tw) // 2)
    if position == "Top":
        y = 16
    elif position == "Center":
        y = (out.height - th) // 2
    else:
        y = max(8, out.height - th - 24)
    draw.text(
        (x, y), text, font=font, fill=color,
        stroke_width=max(1, size // 18), stroke_fill=(0, 0, 0, 170)
    )
    return out.convert("RGB")

@st.cache_resource
def get_background_session():
    from rembg import new_session
    return new_session("u2net")

def remove_background(image):
    from rembg import remove
    rgba = image.convert("RGBA")
    session = get_background_session()
    try:
        res = remove(rgba, session=session, alpha_matting=True)
    except Exception:
        res = remove(rgba, session=session)
    if not isinstance(res, Image.Image):
        res = Image.open(io.BytesIO(res))
    res = res.convert("RGBA")
    alpha = res.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.4))
    res.putalpha(alpha)
    return res

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='padding: 6px 4px 18px;'>
            <div style='font-size: 1.25rem; font-weight: 800; color: #ffffff;'>✦ Image Studio</div>
            <div style='font-size: 0.78rem; color: #64748b;'>Professional Image & Utility Suite</div>
        </div>
    """, unsafe_allow_html=True)

    for cat_name, tools in CATEGORIES.items():
        with st.expander(cat_name, expanded=any(st.session_state.selected_tool == t[0] for t in tools)):
            for name, desc in tools:
                is_active = (st.session_state.selected_tool == name)
                if st.button(name, key=f"nav_{name}", use_container_width=True, type="primary" if is_active else "secondary"):
                    st.session_state.selected_tool = name
                    st.session_state.result_image = None
                    st.rerun()

    st.markdown("---")
    st.caption("Secure in-memory image processing.")

# ---------------------------------------------------------
# HEADER DISPLAY
# ---------------------------------------------------------
tool_name = st.session_state.selected_tool
tool_desc = ""
for cat_tools in CATEGORIES.values():
    for name, desc in cat_tools:
        if name == tool_name:
            tool_desc = desc
            break

st.markdown(f"""
<div class="studio-hero">
    <span class="studio-badge">Creative Workspace</span>
    <h1>{tool_name}</h1>
    <p>{tool_desc}</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2-COLUMN WORKSPACE: [CONTROLS & SETTINGS] | [CANVAS & EXPORT]
# ---------------------------------------------------------
controls_col, canvas_col = st.columns([1, 1.25], gap="large")

with controls_col:
    # Card 1: Input & Optional Aspect Cropping
    with st.container(border=True):
        st.markdown("#### ① Source Image")
        uploaded = st.file_uploader(
            "Upload base photo (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            key=f"file_{tool_name}"
        )
        original = load_image(uploaded)

        if original is not None:
            with st.expander("✂️ Crop & Framing", expanded=False):
                crop_mode = st.selectbox(
                    "Aspect Ratio",
                    ["Original", "Square (1:1)", "Portrait (4:5)", "Landscape (16:9)", "Story/Reel (9:16)"],
                    key=f"crop_{tool_name}"
                )
                if crop_mode != "Original":
                    ratios = {"Square (1:1)": (1, 1), "Portrait (4:5)": (4, 5), "Landscape (16:9)": (16, 9), "Story/Reel (9:16)": (9, 16)}
                    tw, th = ratios[crop_mode]
                    target_ratio = tw / th
                    cur_ratio = original.width / original.height
                    if cur_ratio > target_ratio:
                        nw = max(1, int(original.height * target_ratio))
                        x = (original.width - nw) // 2
                        original = original.crop((x, 0, x + nw, original.height))
                    else:
                        nh = max(1, int(original.width / target_ratio))
                        y = (original.height - nh) // 2
                        original = original.crop((0, y, original.width, y + nh))

    # Card 2: Active Tool Control Rack
    with st.container(border=True):
        st.markdown("#### ② Adjustments & Actions")

        # 1. Image Enhancement
        if tool_name == "Image Enhancement":
            b = st.slider("Brightness", -100, 100, 0, 5)
            c = st.slider("Contrast", -100, 100, 0, 5)
            s = st.slider("Saturation", -100, 100, 0, 5)
            sh = st.slider("Sharpness", -100, 100, 0, 5)

            if original:
                res = ImageEnhance.Brightness(original).enhance(max(0.0, 1.0 + b / 100))
                res = ImageEnhance.Contrast(res).enhance(max(0.0, 1.0 + c / 100))
                res = ImageEnhance.Color(res).enhance(max(0.0, 1.0 + s / 100))
                res = ImageEnhance.Sharpness(res).enhance(max(0.0, 1.0 + sh / 100))
                save_result(res, "enhanced-image.png")

        # 2. Black & White
        elif tool_name == "Black & White":
            contrast = st.slider("Contrast Factor", 0.5, 2.5, 1.1, 0.05)
            if original:
                res = ImageOps.grayscale(original).convert("RGB")
                res = ImageEnhance.Contrast(res).enhance(contrast)
                save_result(res, "monochrome.png")

        # 3. File Size Compressor
        elif tool_name == "File Size Compressor":
            target_kb = st.number_input("Target file budget (KB)", min_value=30, max_value=8000, value=300, step=50)
            if original:
                best_buf = None
                achieved_kb = 0
                for quality in range(95, 10, -5):
                    buf = io.BytesIO()
                    original.save(buf, format="JPEG", optimize=True, quality=quality)
                    achieved_kb = len(buf.getvalue()) / 1024
                    best_buf = buf
                    if achieved_kb <= target_kb:
                        break
                compressed_img = Image.open(best_buf)
                st.info(f"Target: {target_kb} KB | Achieved: {achieved_kb:.1f} KB")
                save_result(compressed_img, "compressed.jpg")

        # 4. Color Splash
        elif tool_name == "Color Splash":
            color_choice = st.selectbox("Color to preserve", ["Red", "Green", "Blue", "Yellow", "Orange"])
            tolerance = st.slider("Hue range tolerance", 5, 40, 18)
            hue_map = {"Red": 0, "Orange": 15, "Yellow": 28, "Green": 60, "Blue": 115}
            if original:
                img_np = np.array(original.convert("RGB"))
                hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
                target_hue = hue_map[color_choice]

                if color_choice == "Red":
                    mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([tolerance, 255, 255]))
                    mask2 = cv2.inRange(hsv, np.array([180 - tolerance, 50, 50]), np.array([180, 255, 255]))
                    mask = cv2.bitwise_or(mask1, mask2)
                else:
                    lower = np.array([max(0, target_hue - tolerance), 50, 50])
                    upper = np.array([min(179, target_hue + tolerance), 255, 255])
                    mask = cv2.inRange(hsv, lower, upper)

                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                splash = np.where(mask[:, :, None] > 0, img_np, gray_rgb)
                save_result(Image.fromarray(splash), "color-splash.png")

        # 5. Color to Sketch
        elif tool_name == "Color to Sketch":
            blur = st.slider("Sketch stroke softness", 1, 21, 7, step=2)
            if original:
                gray = ImageOps.grayscale(original)
                inverted = ImageOps.invert(gray).filter(ImageFilter.GaussianBlur(radius=blur))
                a = np.asarray(gray, dtype=np.float32)
                b = np.asarray(inverted, dtype=np.float32)
                dodge = np.minimum(255, a * 255 / np.maximum(1, 255 - b))
                save_result(Image.fromarray(np.uint8(dodge.clip(0, 255))).convert("RGB"), "pencil-sketch.png")

        # 6. Image Blending
        elif tool_name == "Image Blending":
            second_upload = st.file_uploader("Second overlay image", type=["jpg", "jpeg", "png", "webp"], key="blend_sec")
            opacity = st.slider("Overlay opacity (%)", 0, 100, 50)
            mode = st.selectbox("Blend mode", ["Normal", "Multiply", "Screen", "Difference", "Darken", "Lighten"])
            if original and second_upload:
                second = load_image(second_upload)
                if second:
                    base = original.convert("RGBA")
                    overlay = fit_image(second, original.size).convert("RGBA")
                    overlay.putalpha(round(opacity * 255 / 100))

                    if mode == "Normal":
                        res = Image.alpha_composite(base, overlay)
                    else:
                        rgb_a = np.asarray(original.convert("RGB"), dtype=np.float32)
                        rgb_b = np.asarray(fit_image(second, original.size), dtype=np.float32)
                        if mode == "Multiply":
                            arr = rgb_a * rgb_b / 255
                        elif mode == "Screen":
                            arr = 255 - (255 - rgb_a) * (255 - rgb_b) / 255
                        elif mode == "Difference":
                            arr = np.abs(rgb_a - rgb_b)
                        elif mode == "Darken":
                            arr = np.minimum(rgb_a, rgb_b)
                        else:
                            arr = np.maximum(rgb_a, rgb_b)
                        blended = Image.fromarray(np.uint8(arr.clip(0, 255))).convert("RGBA")
                        res = Image.blend(base, blended, opacity / 100)
                    save_result(res.convert("RGB"), "blended-image.png")

        # 7. AI Background Change
        elif tool_name == "AI Background Change":
            bg_upload = st.file_uploader("Optional: background image", type=["jpg", "jpeg", "png", "webp"], key="bg_up")
            bg_color = st.color_picker("Background color", "#e2e8f0")
            scale = st.slider("Subject scale (%)", 50, 150, 100)

            if original and st.button("Generate Background Swap", type="primary"):
                with st.spinner("Segmenting subject with AI..."):
                    cutout = remove_background(original)
                    if bg_upload is not None:
                        bg_img = load_image(bg_upload)
                        canvas = fit_image(bg_img, original.size).convert("RGBA")
                    else:
                        rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                        canvas = Image.new("RGBA", original.size, rgb + (255,))

                    subject = cutout
                    if scale != 100:
                        nw = max(1, round(subject.width * scale / 100))
                        nh = max(1, round(subject.height * scale / 100))
                        subject = subject.resize((nw, nh), Image.Resampling.LANCZOS)

                    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                    x = (canvas.width - subject.width) // 2
                    y = (canvas.height - subject.height) // 2
                    layer.paste(subject, (x, y), subject)
                    res = Image.alpha_composite(canvas, layer).convert("RGB")
                    save_result(res, "bg-changed.png")

        # 8 & 9. Photo Sheets
        elif tool_name in ["Passport Photo Sheet", "Stamp Photo Maker"]:
            is_pass = (tool_name == "Passport Photo Sheet")
            default_w, default_h = (35, 45) if is_pass else (25, 30)
            c1, c2 = st.columns(2)
            with c1:
                pw = st.number_input("Width (mm)", 10, 100, default_w)
                copies = st.number_input("Copies", 1, 48, 8)
            with c2:
                ph = st.number_input("Height (mm)", 10, 100, default_h)
                paper = st.selectbox("Paper Standard", ["A4", "Letter"])

            if original and st.button("Generate Printable Sheet", type="primary"):
                dpi = 300
                mm_to_px = dpi / 25.4
                page_mm = (210, 297) if paper == "A4" else (216, 279)
                W, H = round(page_mm[0] * mm_to_px), round(page_mm[1] * mm_to_px)
                fw, fh = round(pw * mm_to_px), round(ph * mm_to_px)
                gap, margin = round(4 * mm_to_px), round(8 * mm_to_px)
                cols = max(1, (W - 2 * margin + gap) // (fw + gap))
                rows = max(1, (H - 2 * margin + gap) // (fh + gap))

                sheet = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(sheet)
                thumb = fit_image(original, (fw, fh))
                for i in range(min(copies, cols * rows)):
                    x = margin + (i % cols) * (fw + gap)
                    y = margin + (i // cols) * (fh + gap)
                    sheet.paste(thumb, (x, y))
                    draw.rectangle((x, y, x + fw - 1, y + fh - 1), outline="#d1d5db", width=2)
                save_result(sheet, f"{tool_name.lower().replace(' ', '-')}.png")

        # 10. Image Geotagging
        elif tool_name == "Image Geotagging":
            location = st.text_input("Location name", "Bengaluru, India")
            coords = st.text_input("Coordinates", "12.9716° N, 77.5946° E")
            tag_date = st.date_input("Date", value=date.today())
            pos = st.selectbox("Position", ["Bottom", "Top"])

            if original:
                res = original.copy()
                lines = [l.strip() for l in [location, coords, tag_date.isoformat()] if l.strip()]
                draw = ImageDraw.Draw(res)
                font = make_font(max(15, res.width // 36))
                pad = max(10, res.width // 75)
                line_h = max(20, res.width // 30)
                box_h = len(lines) * line_h + 2 * pad
                y = 12 if pos == "Top" else max(10, res.height - box_h - 12)
                draw.rectangle((0, y, res.width, y + box_h), fill=(0, 0, 0))
                for i, text_line in enumerate(lines):
                    draw.text((pad, y + pad + i * line_h), text_line, fill="#ffffff", font=font)
                save_result(res, "geotagged.png")

        # 11. Add Date & Text
        elif tool_name == "Add Date & Text":
            text = st.text_input("Caption or watermark", "Studio Watermark")
            add_dt = st.checkbox("Include today's date")
            pos = st.selectbox("Position", ["Bottom", "Top", "Center"])
            f_size = st.slider("Font size", 12, 120, 36)
            col = st.color_picker("Text color", "#FFFFFF")

            if original:
                caption = f"{text} {date.today().isoformat()}" if add_dt else text
                res = add_text_overlay(original, caption, pos, col, f_size)
                save_result(res, "text-overlay.png")

        # 12. Collage Maker
        elif tool_name == "Collage Maker":
            extras = st.file_uploader("Upload additional photos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="col_extra")
            cols_grid = st.selectbox("Columns", [2, 3, 4], index=1)
            cell_size = st.selectbox("Tile size (px)", [250, 400, 600], index=1)
            spacing = st.slider("Spacing", 0, 40, 10)

            if original:
                images = [original] + [load_image(f) for f in (extras or []) if load_image(f) is not None]
                if st.button("Generate Collage", type="primary"):
                    rows_grid = math.ceil(len(images) / cols_grid)
                    w = cols_grid * cell_size + (cols_grid + 1) * spacing
                    h = rows_grid * cell_size + (rows_grid + 1) * spacing
                    collage = Image.new("RGB", (w, h), "white")
                    for i, img in enumerate(images):
                        x = spacing + (i % cols_grid) * (cell_size + spacing)
                        y = spacing + (i // cols_grid) * (cell_size + spacing)
                        collage.paste(fit_image(img, (cell_size, cell_size)), (x, y))
                    save_result(collage, "collage.png")

        # 13. Wallpaper Designer
        elif tool_name == "Wallpaper Designer":
            preset = st.selectbox("Screen format", ["Phone (1080 × 1920)", "Desktop (1920 × 1080)", "Square (1080 × 1080)"])
            bg_col = st.color_picker("Canvas background", "#18181b")
            title = st.text_input("Title overlay", "MINIMALIST")
            dims = {"Phone (1080 × 1920)": (1080, 1920), "Desktop (1920 × 1080)": (1920, 1080), "Square (1080 × 1080)": (1080, 1080)}

            if st.button("Generate Wallpaper", type="primary"):
                size = dims[preset]
                rgb = tuple(int(bg_col[i:i+2], 16) for i in (1, 3, 5))
                wp = Image.new("RGB", size, rgb)
                if original:
                    photo = fit_image(original, (int(size[0] * 0.82), int(size[1] * 0.65)))
                    wp.paste(photo, ((size[0] - photo.width) // 2, int(size[1] * 0.08)))
                wp = add_text_overlay(wp, title, "Bottom", "#FFFFFF", max(28, size[0] // 16))
                save_result(wp, "wallpaper.png")

        # 14. Image Similarity
        elif tool_name == "Image Similarity":
            sec_sim = st.file_uploader("Second image for comparison", type=["jpg", "jpeg", "png", "webp"], key="sim_sec")
            if original and sec_sim:
                second = load_image(sec_sim)
                if second:
                    size = (160, 160)
                    a = np.asarray(fit_image(original, size), dtype=np.float32)
                    b = np.asarray(fit_image(second, size), dtype=np.float32)
                    score = max(0.0, 100.0 * (1.0 - np.mean(np.abs(a - b)) / 255.0))
                    st.metric("Similarity score", f"{score:.1f}%")

                    diff = Image.fromarray(np.uint8(np.abs(a - b).mean(axis=2).clip(0, 255)))
                    save_result(diff, "difference-map.png")

# ---------------------------------------------------------
# DIGITAL CANVAS & INSTANT EXPORT COLUMN
# ---------------------------------------------------------
with canvas_col:
    with st.container(border=True):
        st.markdown("#### Preview & Instant Export")

        if original is None:
            st.markdown("""
                <div style='text-align: center; padding: 50px 16px; color: #94a3b8;'>
                    <div style='font-size: 2.5rem; margin-bottom: 8px;'>📷</div>
                    <div style='font-weight: 600; color: #475569;'>No Image Loaded</div>
                    <div style='font-size: 0.85rem;'>Upload a source photo on the left to activate this studio canvas.</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            tab_edited, tab_original = st.tabs(["✨ Edited Result", "🖼 Original"])
            with tab_edited:
                if st.session_state.result_image is not None:
                    st.image(st.session_state.result_image, use_container_width=True)
                else:
                    st.image(original, use_container_width=True)

            with tab_original:
                st.image(original, use_container_width=True)

            st.markdown("---")
            if st.session_state.result_image is not None:
                st.download_button(
                    label=f"⬇ Download Output ({st.session_state.result_name})",
                    data=png_bytes(st.session_state.result_image),
                    file_name=st.session_state.result_name,
                    mime="image/png",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.button("⬇ Download Output", disabled=True, use_container_width=True)
