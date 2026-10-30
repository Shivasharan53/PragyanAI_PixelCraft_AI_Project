import io
import math
from datetime import datetime, date
import numpy as np
import cv2
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Image Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOOLS = [
    ("1", "✦", "Image Enhancement", "Adjust brightness, contrast, color and sharpness."),
    ("2", "🥞", "Image Blending", "Blend two images using opacity and blend modes."),
    ("3", "✂️", "AI Background Change", "Remove a background with precision and add a replacement."),
    ("4", "◐", "Black & White", "Convert color photos to monochrome with tone controls."),
    ("5", "✏️", "Color to Sketch", "Create a pencil-style realistic drawing."),
    ("6", "🪪", "Passport Photo Sheet", "Arrange standard passport photos for printing."),
    ("7", "👤", "Stamp Photo Maker", "Create repeated small photo prints on sheet."),
    ("8", "🖼", "Image Similarity", "Compare two images and inspect visual differences."),
    ("9", "🔤", "Add Date & Text", "Add movable captions, dates, custom fonts and watermarks."),
    ("10", "📍", "Image Geotagging", "Add visible location, country, coordinates and GPS badges."),
    ("11", "⊞", "Collage Maker", "Combine multiple photos into a clean grid."),
    ("12", "📱", "Wallpaper Designer", "Design tailored phone, desktop or square wallpapers."),
]

# ---------------------------------------------------------
# EXACT DESIGN SYSTEM (MATCHING REFERENCE SCREENSHOT)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

:root {
    --primary: #6c5ce7;
    --primary-gradient: linear-gradient(110deg, #7c58f9 0%, #6342ea 100%);
    --bg-main: #f4f6fc;
    --card-border: #e3e7f5;
    --sidebar-bg: #10182d;
}

.stApp {
    background-color: var(--bg-main) !important;
    color: #17213b;
}

/* Sidebar Styling matching screenshot */
section[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid #1e2842 !important;
}

section[data-testid="stSidebar"] * {
    color: #c5cde8 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #b7c2e2 !important;
    border-radius: 10px !important;
    padding: 0.55rem 0.85rem !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    display: flex !important;
    justify-content: flex-start !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #192440 !important;
    color: #ffffff !important;
    transform: translateX(3px) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: #ffffff !important;
    font-weight: 650 !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(108, 92, 231, 0.35) !important;
}

/* Studio Hero Header */
.hero-container {
    background: linear-gradient(115deg, #ffffff 0%, #f4efff 50%, #eaf3ff 100%);
    border: 1px solid #e3e6f7;
    border-radius: 20px;
    padding: 22px 28px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 24px rgba(31, 43, 79, 0.04);
}

.tool-badge {
    background: #ebe4ff;
    color: #6c52ea;
    font-size: 0.72rem;
    font-weight: 750;
    padding: 4px 12px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #151d36;
    margin: 8px 0 4px 0;
    letter-spacing: -0.03em;
}

.hero-desc {
    color: #636f8e;
    font-size: 0.96rem;
    margin: 0;
}

.hero-subdesc {
    color: #8c97b5;
    font-size: 0.78rem;
    margin-top: 8px;
    letter-spacing: 0.02em;
}

/* Card Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(22, 33, 62, 0.035) !important;
    padding: 1.1rem !important;
}

/* Step Badges (1, 2, 3) */
.step-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.02rem;
    font-weight: 750;
    color: #17213b;
    margin-bottom: 4px;
}

.step-num {
    background: #6c52ea;
    color: #ffffff;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 800;
}

/* Primary Purple Buttons */
.stButton > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 650 !important;
    min-height: 44px !important;
    box-shadow: 0 4px 14px rgba(108, 92, 231, 0.28) !important;
}

.stButton > button[kind="primary"]:hover {
    filter: brightness(1.05) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Buttons */
.stButton > button[kind="secondary"] {
    background: #f0edff !important;
    color: #5d41e6 !important;
    border: 1px solid #dcd4ff !important;
    border-radius: 11px !important;
    font-weight: 600 !important;
    min-height: 42px !important;
}

/* Sliders */
[data-testid="stSlider"] [role="slider"] {
    background-color: #6c52ea !important;
    border-color: #6c52ea !important;
}

/* File Uploader Box */
[data-testid="stFileUploaderDropzone"] {
    background: #faf8ff !important;
    border: 1.8px dashed #c3b8ff !important;
    border-radius: 14px !important;
}

/* Image rounding */
div[data-testid="stImage"] img {
    border-radius: 12px;
    border: 1px solid #e7ebf7;
}
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
    st.session_state.result_name = "enhanced-image.png"

# ---------------------------------------------------------
# CORE IMAGE & AI HELPERS
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

def get_font_by_choice(style, size):
    font_map = {
        "Modern Sans": ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Arial.ttf"],
        "Classic Serif": ["DejaVuSerif-Bold.ttf", "Times.ttf", "DejaVuSerif.ttf"],
        "Monospace": ["DejaVuSansMono-Bold.ttf", "Courier.ttf", "DejaVuSansMono.ttf"],
    }
    candidates = font_map.get(style, ["DejaVuSans.ttf"])
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()

@st.cache_resource
def get_bg_model_session(model_name="u2net"):
    try:
        from rembg import new_session
        return new_session(model_name)
    except Exception:
        return None

def remove_background_ai(image, model_choice="u2net"):
    from rembg import remove
    session = get_bg_model_session(model_choice)
    rgba = image.convert("RGBA")

    # High precision alpha matting
    try:
        cutout = remove(
            rgba,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=245,
            alpha_matting_background_threshold=15,
            alpha_matting_erode_size=8
        )
    except Exception:
        cutout = remove(rgba, session=session)

    if not isinstance(cutout, Image.Image):
        cutout = Image.open(io.BytesIO(cutout))

    cutout = cutout.convert("RGBA")
    # Clean edge anti-aliasing
    alpha = cutout.getchannel("A").filter(ImageFilter.GaussianBlur(radius=0.45))
    cutout.putalpha(alpha)
    return cutout

def save_result(image, filename="studio-output.png"):
    st.session_state.result_image = image.copy()
    st.session_state.result_name = filename

# ---------------------------------------------------------
# SIDEBAR (MATCHING SCREENSHOT)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='padding:12px 6px 20px'>
            <div style='font-size:26px;font-weight:800;color:#ffffff;display:flex;align-items:center;gap:8px;'>
                <span>✦</span> Image Studio
            </div>
            <div style='color:#8c98be;font-size:12.5px;margin-top:4px;'>Your photos, your creativity.</div>
        </div>
        <div style='color:#7584af;font-size:11px;font-weight:700;letter-spacing:1px;margin:8px 0 10px 8px;'>IMAGE TOOLS</div>
    """, unsafe_allow_html=True)

    for num, icon, name, desc in TOOLS:
        is_sel = (st.session_state.selected_tool == name)
        btn_label = f"{icon}  {num}  {name}"
        if st.button(btn_label, key=f"side_{num}", use_container_width=True, type="primary" if is_sel else "secondary"):
            st.session_state.selected_tool = name
            st.session_state.result_image = None
            st.rerun()

    st.markdown("---")
    st.markdown("""
        <div style='background:#18233f;border:1px solid #233154;border-radius:12px;padding:12px;'>
            <div style='font-size:16px;'>💡</div>
            <div style='font-size:12px;font-weight:600;color:#e1e7fa;margin-top:4px;'>Simple. Creative. Powerful.</div>
            <div style='font-size:11px;color:#8d9bbd;margin-top:2px;'>Edit, enhance and transform your photos in one place.</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# HERO BANNER (MATCHING SCREENSHOT)
# ---------------------------------------------------------
tool_info = next(t for t in TOOLS if t[2] == st.session_state.selected_tool)
tool_num, tool_icon, tool_name, tool_desc = tool_info

st.markdown(f"""
<div class="hero-container">
    <div>
        <span class="tool-badge">IMAGE STUDIO / TOOL {tool_num}</span>
        <div class="hero-title">{tool_name}</div>
        <div class="hero-desc">{tool_desc}</div>
        <div class="hero-subdesc">Upload · Customize · Preview · Export</div>
    </div>
    <div style="display:flex;align-items:center;gap:12px;background:rgba(255,255,255,0.7);padding:8px 14px;border-radius:14px;border:1px solid #e3e7f4;">
        <div style="font-size:12px;font-weight:700;color:#6c52ea;text-align:center;">
            ⚡ ACTIVE<br><span style="color:#202a46;">READY</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TOOL WORKSPACE
# ---------------------------------------------------------

# =========================================================
# 1. IMAGE ENHANCEMENT (EXACT 3-CARD LAYOUT AS SCREENSHOT)
# =========================================================
if tool_name == "Image Enhancement":
    c1, c2, c3 = st.columns([1.1, 1.25, 1.15], gap="medium")

    # Card 1: Upload
    with c1:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">1</span> Upload your image</div>', unsafe_allow_html=True)
            st.caption("Start with a clear JPG, PNG or WEBP photo.")
            uploaded = st.file_uploader(
                "Drag and drop your image here",
                type=["jpg", "jpeg", "png", "webp"],
                key="enh_up",
                help="Supports JPG, PNG, WEBP • Max 10MB"
            )
            original = load_image(uploaded)
            if original is not None:
                st.image(original, caption=f"{original.width} × {original.height} px", use_container_width=True)

    # Card 2: Crop & Framing
    with c2:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">2</span> Crop & framing (optional)</div>', unsafe_allow_html=True)
            st.caption("Crop the image before enhancement. Leave Original to keep full photo.")

            st.write("**Choose aspect ratio**")
            aspect_choice = st.radio(
                "Aspect ratio selector",
                ["Original", "1:1 Square", "4:5 Portrait", "16:9 Landscape", "9:16 Phone"],
                horizontal=True,
                label_visibility="collapsed"
            )

            st.write("**Adjust crop (remove from edges %)**")
            sl1, sl2 = st.columns(2)
            with sl1:
                crop_top = st.slider("Top", 0, 40, 0)
                crop_bottom = st.slider("Bottom", 0, 40, 0)
            with sl2:
                crop_left = st.slider("Left", 0, 40, 0)
                crop_right = st.slider("Right", 0, 40, 0)

            # Apply Cropping
            if original is not None:
                if aspect_choice != "Original":
                    ratio_dict = {
                        "1:1 Square": (1, 1),
                        "4:5 Portrait": (4, 5),
                        "16:9 Landscape": (16, 9),
                        "9:16 Phone": (9, 16)
                    }
                    rw, rh = ratio_dict[aspect_choice]
                    target_ratio = rw / rh
                    curr_ratio = original.width / original.height
                    if curr_ratio > target_ratio:
                        nw = max(1, int(original.height * target_ratio))
                        x = (original.width - nw) // 2
                        original = original.crop((x, 0, x + nw, original.height))
                    else:
                        nh = max(1, int(original.width / target_ratio))
                        y = (original.height - nh) // 2
                        original = original.crop((0, y, original.width, y + nh))

                if any([crop_top, crop_bottom, crop_left, crop_right]):
                    l = int(original.width * crop_left / 100)
                    t = int(original.height * crop_top / 100)
                    r = original.width - int(original.width * crop_right / 100)
                    b = original.height - int(original.height * crop_bottom / 100)
                    if (r - l) >= 10 and (b - t) >= 10:
                        original = original.crop((l, t, r, b))

    # Card 3: Settings
    with c3:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">3</span> Enhancement settings</div>', unsafe_allow_html=True)
            st.caption("Adjust the image to get the best result.")

            brightness = st.slider("Brightness", -100, 100, 0, 5, key="b_sl")
            contrast = st.slider("Contrast", -100, 100, 0, 5, key="c_sl")
            saturation = st.slider("Saturation", -100, 100, 0, 5, key="s_sl")
            color_int = st.slider("Color", -100, 100, 0, 5, key="col_sl")
            sharpness = st.slider("Sharpness", -100, 100, 0, 5, key="sh_sl")

            apply_enh = st.button("✦ Apply Enhancement", type="primary", use_container_width=True)

    # Preview & Download Bottom Grid (Matching Screenshot)
    if original is not None:
        result = ImageEnhance.Brightness(original).enhance(max(0.0, 1.0 + brightness / 100))
        result = ImageEnhance.Contrast(result).enhance(max(0.0, 1.0 + contrast / 100))
        result = ImageEnhance.Color(result).enhance(max(0.0, 1.0 + saturation / 100))
        result = ImageEnhance.Color(result).enhance(max(0.0, 1.0 + color_int / 100))
        result = ImageEnhance.Sharpness(result).enhance(max(0.0, 1.0 + sharpness / 100))

        if apply_enh:
            save_result(result, "enhanced-photo.png")
            st.success("Enhancement applied.")

        st.markdown("<br>", unsafe_allow_html=True)
        prev_col, action_col = st.columns([2.35, 1.15], gap="medium")

        with prev_col:
            with st.container(border=True):
                p_left, p_right = st.columns(2, gap="medium")
                with p_left:
                    st.markdown("**Original Image**")
                    st.image(original, use_container_width=True)
                with p_right:
                    st.markdown("**Enhanced Preview**")
                    st.image(result, use_container_width=True)

        with action_col:
            with st.container(border=True):
                st.markdown("**Download & Actions**")
                st.caption("Once you are happy with the result, download or reset.")

                download_target = st.session_state.result_image if st.session_state.result_image is not None else result
                st.download_button(
                    "⬇ Download Image",
                    data=png_bytes(download_target),
                    file_name="enhanced-image.png",
                    mime="image/png",
                    type="primary",
                    use_container_width=True
                )

                a1, a2 = st.columns(2)
                with a1:
                    if st.button("↻ Reset All", use_container_width=True):
                        st.session_state.result_image = None
                        st.rerun()
                with a2:
                    if st.button("Use Original", use_container_width=True):
                        save_result(original, "original.png")
                        st.rerun()

                st.markdown("""
                    <div style='background:#f6f8ff;border-radius:12px;padding:12px;color:#374261;font-size:12px;margin-top:14px;'>
                        <b>💡 Tips</b><br>
                        • Increase contrast to make details clearer.<br>
                        • Boost saturation for more vivid colors.<br>
                        • Use a higher sharpness value for crisper images.
                    </div>
                """, unsafe_allow_html=True)

# =========================================================
# 3. AI BACKGROUND CHANGE (PRECISION MATTING FIX)
# =========================================================
elif tool_name == "AI Background Change":
    left_c, right_c = st.columns([1, 1.25], gap="large")

    with left_c:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">1</span> Upload subject photo</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload portrait or subject", type=["jpg", "jpeg", "png", "webp"], key="bg_up")
            original = load_image(uploaded)

        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">2</span> Replacement background</div>', unsafe_allow_html=True)
            bg_mode = st.radio("Background Type", ["Solid Color", "Custom Image", "Transparent Cutout (PNG)"], horizontal=True)

            bg_image = None
            bg_color = "#f4f6fc"
            if bg_mode == "Solid Color":
                bg_color = st.color_picker("Pick background color", "#ffffff")
            elif bg_mode == "Custom Image":
                bg_file = st.file_uploader("Upload background image", type=["jpg", "png", "webp"], key="bg_img_file")
                bg_image = load_image(bg_file)

            st.write("**Subject adjustments**")
            scale = st.slider("Subject Scale (%)", 50, 150, 100)
            shift_x = st.slider("Move Left / Right", -300, 300, 0)
            shift_y = st.slider("Move Up / Down", -300, 300, 0)

            run_btn = st.button("✂️ Remove & Replace Background", type="primary", use_container_width=True)

    with right_c:
        with st.container(border=True):
            st.markdown("#### Preview & Result")
            if original is None:
                st.info("Upload an image on the left to start background removal.")
            else:
                if run_btn:
                    with st.spinner("AI is cleanly segmenting the subject (hair & edge anti-aliasing)..."):
                        cutout = remove_background_ai(original)

                        if bg_mode == "Transparent Cutout (PNG)":
                            final_bg = cutout
                        else:
                            if bg_mode == "Custom Image" and bg_image is not None:
                                canvas = fit_image(bg_image, original.size).convert("RGBA")
                            else:
                                rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
                                canvas = Image.new("RGBA", original.size, rgb + (255,))

                            subject = cutout
                            if scale != 100:
                                nw = max(1, round(subject.width * scale / 100))
                                nh = max(1, round(subject.height * scale / 100))
                                subject = subject.resize((nw, nh), Image.Resampling.LANCZOS)

                            layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                            x = (canvas.width - subject.width) // 2 + shift_x
                            y = (canvas.height - subject.height) // 2 + shift_y
                            layer.paste(subject, (x, y), subject)
                            final_bg = Image.alpha_composite(canvas, layer).convert("RGB")

                        save_result(final_bg, "bg-removed.png")
                        st.success("Background replaced cleanly!")

                if st.session_state.result_image is not None:
                    st.image(st.session_state.result_image, use_container_width=True)
                    st.download_button(
                        "⬇ Download Cutout / Result",
                        data=png_bytes(st.session_state.result_image),
                        file_name="bg-replaced.png",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.image(original, caption="Original Image", use_container_width=True)

# =========================================================
# 9. ADD DATE & TEXT (FREE MOVEMENT & FONTS)
# =========================================================
elif tool_name == "Add Date & Text":
    left_c, right_c = st.columns([1, 1.25], gap="large")

    with left_c:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">1</span> Upload Image</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"], key="txt_up")
            original = load_image(uploaded)

        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">2</span> Typography & Styling</div>', unsafe_allow_html=True)
            text_val = st.text_input("Caption / Watermark text", "IMAGE STUDIO")
            add_date = st.checkbox("Include Date Stamp", value=False)
            if add_date:
                chosen_date = st.date_input("Date", value=date.today())
                text_val = f"{text_val} • {chosen_date.strftime('%b %d, %Y')}"

            c_f1, c_f2 = st.columns(2)
            with c_f1:
                font_style = st.selectbox("Font Style", ["Modern Sans", "Classic Serif", "Monospace"])
                font_size = st.slider("Font Size", 14, 140, 42)
            with c_f2:
                text_color = st.color_picker("Text Color", "#ffffff")
                bg_box = st.checkbox("Add Background Pill", value=True)

            st.write("**Free Position Movement (Anywhere on Canvas)**")
            pos_x = st.slider("X Position (Horizontal %)", 0, 100, 50)
            pos_y = st.slider("Y Position (Vertical %)", 0, 100, 85)

    with right_c:
        with st.container(border=True):
            st.markdown("#### Live Preview & Download")
            if original:
                out = original.convert("RGBA").copy()
                draw = ImageDraw.Draw(out)
                font = get_font_by_choice(font_style, font_size)

                # Calculate bounding box
                bbox = draw.textbbox((0, 0), text_val, font=font, stroke_width=2)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

                # Map % position to pixel coordinate
                target_x = int((out.width - tw) * (pos_x / 100.0))
                target_y = int((out.height - th) * (pos_y / 100.0))

                if bg_box:
                    pad_x, pad_y = 16, 8
                    draw.rounded_rectangle(
                        (target_x - pad_x, target_y - pad_y, target_x + tw + pad_x, target_y + th + pad_y),
                        radius=8,
                        fill=(0, 0, 0, 160)
                    )

                draw.text(
                    (target_x, target_y),
                    text_val,
                    font=font,
                    fill=text_color,
                    stroke_width=max(1, font_size // 22),
                    stroke_fill=(0, 0, 0, 200)
                )

                rendered = out.convert("RGB")
                st.image(rendered, use_container_width=True)
                save_result(rendered, "text-overlay.png")

                st.download_button(
                    "⬇ Download Image with Text",
                    data=png_bytes(rendered),
                    file_name="watermarked-studio.png",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("Upload an image on the left to add movable text.")

# =========================================================
# 10. IMAGE GEOTAGGING (PROFESSIONAL GPS WATERMARK)
# =========================================================
elif tool_name == "Image Geotagging":
    left_c, right_c = st.columns([1, 1.25], gap="large")

    with left_c:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">1</span> Upload photo</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png", "webp"], key="geo_up")
            original = load_image(uploaded)

        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">2</span> GPS Location & Details</div>', unsafe_allow_html=True)
            city = st.text_input("City / Landmark", "Bengaluru")
            state_country = st.text_input("State, Country", "Karnataka, India")
            coords = st.text_input("Coordinates", "12°58'23.2\"N 77°35'45.4\"E")

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                geo_date = st.date_input("Date", value=date.today())
            with col_d2:
                badge_pos = st.selectbox("Badge Location", ["Bottom-Left", "Bottom-Right", "Top-Left", "Top-Right"])

            badge_style = st.selectbox("Design Theme", ["Modern Dark Glass", "Clean White Box", "Classic Road Ribbon"])

    with right_c:
        with st.container(border=True):
            st.markdown("#### Geotagged Camera Preview")
            if original:
                geo_img = original.copy()
                draw = ImageDraw.Draw(geo_img)

                f_size = max(16, geo_img.width // 45)
                font_bold = get_font_by_choice("Modern Sans", int(f_size * 1.15))
                font_regular = get_font_by_choice("Modern Sans", f_size)

                line1 = f"📍 {city}, {state_country}"
                line2 = f"🌐 {coords}"
                line3 = f"📅 {geo_date.strftime('%A, %d %B %Y')} • {datetime.now().strftime('%I:%M %p')}"

                pad = 16
                line_spacing = int(f_size * 1.35)
                box_w = max(int(geo_img.width * 0.52), 340)
                box_h = line_spacing * 3 + pad * 2

                # Coordinates placement
                if "Bottom" in badge_pos:
                    by = geo_img.height - box_h - 24
                else:
                    by = 24

                if "Left" in badge_pos:
                    bx = 24
                else:
                    bx = geo_img.width - box_w - 24

                # Styling
                if badge_style == "Modern Dark Glass":
                    bg_col = (15, 23, 42)
                    text_main = "#ffffff"
                    text_sub = "#94a3b8"
                elif badge_style == "Clean White Box":
                    bg_col = (255, 255, 255)
                    text_main = "#0f172a"
                    text_sub = "#475569"
                else:
                    bg_col = (0, 0, 0)
                    text_main = "#facc15"
                    text_sub = "#ffffff"

                draw.rounded_rectangle((bx, by, bx + box_w, by + box_h), radius=12, fill=bg_col)
                draw.text((bx + pad, by + pad), line1, fill=text_main, font=font_bold)
                draw.text((bx + pad, by + pad + line_spacing), line2, fill=text_sub, font=font_regular)
                draw.text((bx + pad, by + pad + line_spacing * 2), line3, fill=text_sub, font=font_regular)

                st.image(geo_img, use_container_width=True)
                save_result(geo_img, "geotagged-photo.png")

                st.download_button(
                    "⬇ Download Geotagged Photo",
                    data=png_bytes(geo_img),
                    file_name="geotagged-camera.png",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("Upload a photo on the left to burn GPS location and date badges.")

# =========================================================
# REMAINING TOOLS: BLENDING, B&W, SKETCH, SHEETS, ETC.
# =========================================================
else:
    left_c, right_c = st.columns([1, 1.25], gap="large")

    with left_c:
        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">1</span> Source Image</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"], key=f"f_{tool_name}")
            original = load_image(uploaded)

        with st.container(border=True):
            st.markdown('<div class="step-header"><span class="step-num">2</span> Settings</div>', unsafe_allow_html=True)

            if tool_name == "Black & White":
                contrast_val = st.slider("Monochrome Contrast", 0.5, 2.5, 1.15)
                if original:
                    res = ImageOps.grayscale(original).convert("RGB")
                    res = ImageEnhance.Contrast(res).enhance(contrast_val)
                    save_result(res, "monochrome.png")

            elif tool_name == "Color to Sketch":
                softness = st.slider("Sketch Blur Stroke", 1, 21, 7, step=2)
                if original:
                    gray = ImageOps.grayscale(original)
                    inv = ImageOps.invert(gray).filter(ImageFilter.GaussianBlur(radius=softness))
                    a = np.asarray(gray, dtype=np.float32)
                    b = np.asarray(inv, dtype=np.float32)
                    dodge = np.minimum(255, a * 255 / np.maximum(1, 255 - b))
                    res = Image.fromarray(np.uint8(dodge.clip(0, 255))).convert("RGB")
                    save_result(res, "pencil-sketch.png")

            elif tool_name in ["Passport Photo Sheet", "Stamp Photo Maker"]:
                is_p = tool_name == "Passport Photo Sheet"
                pw, ph = (35, 45) if is_p else (25, 30)
                copies = st.number_input("Number of Copies", 1, 36, 8)
                paper = st.selectbox("Paper Format", ["A4", "Letter"])
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
                        draw.rectangle((x, y, x + fw - 1, y + fh - 1), outline="#cbd5e1", width=2)
                    save_result(sheet, "photo-sheet.png")

            elif tool_name == "Collage Maker":
                extras = st.file_uploader("Upload more photos", type=["jpg", "png", "webp"], accept_multiple_files=True)
                cols_n = st.selectbox("Columns", [2, 3, 4], index=1)
                cell = st.selectbox("Tile Size", [250, 400, 600], index=1)
                if original and st.button("Build Collage", type="primary"):
                    imgs = [original] + [load_image(f) for f in (extras or []) if load_image(f) is not None]
                    rows_n = math.ceil(len(imgs) / cols_n)
                    gap = 10
                    cw = cols_n * cell + (cols_n + 1) * gap
                    ch = rows_n * cell + (rows_n + 1) * gap
                    col_canvas = Image.new("RGB", (cw, ch), "white")
                    for i, img in enumerate(imgs):
                        x = gap + (i % cols_n) * (cell + gap)
                        y = gap + (i // cols_n) * (cell + gap)
                        col_canvas.paste(fit_image(img, (cell, cell)), (x, y))
                    save_result(col_canvas, "collage.png")

            elif tool_name == "Wallpaper Designer":
                dim = st.selectbox("Screen Preset", ["Phone (1080 × 1920)", "Desktop (1920 × 1080)", "Square (1080 × 1080)"])
                bg = st.color_picker("Background", "#0f172a")
                title = st.text_input("Title Text", "DREAM BIG")
                dims_map = {"Phone (1080 × 1920)": (1080, 1920), "Desktop (1920 × 1080)": (1920, 1080), "Square (1080 × 1080)": (1080, 1080)}
                if st.button("Generate Wallpaper", type="primary"):
                    size = dims_map[dim]
                    rgb = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
                    wp = Image.new("RGB", size, rgb)
                    if original:
                        p = fit_image(original, (int(size[0] * 0.82), int(size[1] * 0.65)))
                        wp.paste(p, ((size[0] - p.width) // 2, int(size[1] * 0.08)))
                    draw = ImageDraw.Draw(wp)
                    f = get_font_by_choice("Modern Sans", max(30, size[0] // 16))
                    draw.text((size[0] // 2, int(size[1] * 0.82)), title, fill="#ffffff", font=f, anchor="mm")
                    save_result(wp, "wallpaper.png")

            elif tool_name == "Image Similarity":
                s2 = st.file_uploader("Second Image to Compare", type=["jpg", "png", "webp"], key="s_img")
                if original and s2:
                    im2 = load_image(s2)
                    if im2:
                        sz = (160, 160)
                        a = np.asarray(fit_image(original, sz), dtype=np.float32)
                        b = np.asarray(fit_image(im2, sz), dtype=np.float32)
                        score = max(0.0, 100.0 * (1.0 - np.mean(np.abs(a - b)) / 255.0))
                        st.metric("Similarity Match", f"{score:.1f}%")
                        diff = Image.fromarray(np.uint8(np.abs(a - b).mean(axis=2).clip(0, 255)))
                        save_result(diff, "difference-map.png")

            elif tool_name == "Image Blending":
                s2 = st.file_uploader("Second Image to Blend", type=["jpg", "png", "webp"], key="blend_img")
                opacity = st.slider("Opacity (%)", 0, 100, 50)
                if original and s2:
                    im2 = load_image(s2)
                    if im2:
                        base = original.convert("RGBA")
                        overlay = fit_image(im2, original.size).convert("RGBA")
                        overlay.putalpha(round(opacity * 255 / 100))
                        res = Image.alpha_composite(base, overlay).convert("RGB")
                        save_result(res, "blended.png")

    with right_c:
        with st.container(border=True):
            st.markdown("#### Live Preview & Export")
            if original is None:
                st.info("Upload an image on the left panel to begin editing.")
            else:
                if st.session_state.result_image is not None:
                    st.image(st.session_state.result_image, use_container_width=True)
                    st.download_button(
                        f"⬇ Download Output ({st.session_state.result_name})",
                        data=png_bytes(st.session_state.result_image),
                        file_name=st.session_state.result_name,
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.image(original, caption="Current Working Image", use_container_width=True)
