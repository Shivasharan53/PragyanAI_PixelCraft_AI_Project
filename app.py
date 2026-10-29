import io
import math
from datetime import date
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops

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
    ("1", "Image Enhancement", "Adjust brightness, contrast, color and sharpness."),
    ("2", "Image Blending", "Blend two images using opacity and blend modes."),
    ("3", "AI Background Change", "Remove a background and add a replacement."),
    ("4", "Black & White", "Convert color photos to grayscale."),
    ("5", "Color to Sketch", "Create a pencil-style drawing."),
    ("6", "Passport Photo Sheet", "Arrange passport photos for printing."),
    ("7", "Stamp Photo Maker", "Create repeated small photo prints."),
    ("8", "Image Similarity", "Compare two images and inspect differences."),
    ("9", "Add Date & Text", "Add captions, dates and watermarks."),
    ("10", "Image Geotagging", "Add visible location and coordinate labels."),
    ("11", "Collage Maker", "Combine multiple photos in a grid."),
    ("12", "Wallpaper Designer", "Design a phone or desktop wallpaper."),
]

# ---------------------------------------------------------
# CUSTOM DESIGN
# ---------------------------------------------------------
st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background: #f4f6fc; color: #17213b; }
header[data-testid="stHeader"] { background: rgba(244,246,252,.94); }
.block-container { padding-top: 1.05rem; padding-bottom: 2.4rem; max-width: 1680px; }
section[data-testid="stSidebar"] { background: #10182d; border-right: 1px solid #26324e; }
section[data-testid="stSidebar"] * { color: #edf1ff; }
section[data-testid="stSidebar"] .stButton > button { text-align:left; border:1px solid transparent; background:transparent; color:#d6def5; border-radius:11px; min-height:43px; padding:.5rem .7rem; font-size:.88rem; transition:all .18s ease; }
section[data-testid="stSidebar"] .stButton > button:hover { background:#222e4c; border-color:#43517a; transform:translateX(2px); }
section[data-testid="stSidebar"] .stButton > button[kind="primary"], section[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] { background:linear-gradient(110deg,#8058ff,#6545e8); color:white; box-shadow:0 5px 16px rgba(104,75,235,.22); }
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] { background:linear-gradient(110deg,#8058ff,#6545e8); color:white; border:0; border-radius:11px; font-weight:650; box-shadow:0 5px 14px rgba(104,75,235,.16); }
.stButton > button { border-radius:11px; min-height:42px; transition:all .18s ease; }
.stButton > button:hover { border-color:#9d8cff; }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { border-radius:10px; }
.stSlider [data-baseweb="slider"] { padding-top:.35rem; }
.hero { background:linear-gradient(112deg,#ffffff 0%,#f1edff 52%,#e5f3ff 100%); border:1px solid #e3e4f7; padding:25px 28px; border-radius:20px; margin-bottom:20px; box-shadow:0 8px 26px rgba(46,53,94,.045); position:relative; overflow:hidden; }
.hero h1 { margin:8px 0 0; font-size:clamp(1.7rem,2.6vw,2.5rem); letter-spacing:-.045em; color:#17213b; font-weight:800; }
.hero p { color:#65708d; margin:.5rem 0 0; font-size:1.02rem; }
.panel { background:white; border:1px solid #e5e8f3; border-radius:17px; padding:18px; margin-bottom:15px; box-shadow:0 5px 18px rgba(31,43,79,.035); }
.panel-title { font-size:1.05rem; font-weight:750; margin-bottom:12px; color:#202943; }
.muted { color:#737d98; font-size:.88rem; }
.tool-chip { display:inline-block; border-radius:999px; padding:6px 12px; background:#e9e4ff; color:#6545d8; font-size:.76rem; font-weight:750; letter-spacing:.04em; }
div[data-testid="stImage"] img { border-radius:13px; border:1px solid #e9ebf5; }
div[data-testid="stFileUploader"] section { background:#fafaff; border:1.5px dashed #c8c1ff; border-radius:14px; }
div[data-testid="stFileUploader"] button { border-radius:9px; }
div[data-testid="stExpander"] { background:#fff; border:1px solid #e4e7f2; border-radius:14px; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #e5e8f3; padding:14px; border-radius:14px; }
hr { border-color:#e4e7f1; }
.stAlert { border-radius:12px; }
/* Main workspace: force readable contrast for Streamlit-native widgets. */
[data-testid="stMain"] { color: #17213b !important; }
[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] .stMarkdown,
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stMarkdownContainer"] { color: #263451; }
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 { color: #17213b !important; }
/* Keep input text readable in light mode. */
[data-testid="stMain"] input,
[data-testid="stMain"] textarea,
[data-testid="stMain"] [data-baseweb="select"] div,
[data-testid="stMain"] [data-baseweb="select"] span { color: #17213b !important; }
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] { background:#fbfaff !important; border:1.5px dashed #bdb2ff !important; border-radius:14px !important; }
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] * { color:#263451 !important; }
[data-testid="stMain"] [data-testid="stExpander"] { background:#fff !important; border:1px solid #e1e5f2 !important; border-radius:14px !important; }
[data-testid="stMain"] [data-testid="stExpander"] summary,
[data-testid="stMain"] [data-testid="stExpander"] summary * { color:#263451 !important; }
/* Make the top Streamlit toolbar visible without hiding Share or app controls. */
header[data-testid="stHeader"] { background:rgba(244,246,252,.98) !important; }
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] button svg,
header[data-testid="stHeader"] [data-testid="stToolbar"] { color:#263451 !important; fill:#263451 !important; }
/* Avoid accidentally turning main-area buttons white-on-white. */
[data-testid="stMain"] .stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) { color:#4f3cc7 !important; background:#f1edff; border:1px solid #e0d9ff; }
[data-testid="stMain"] .stButton > button[kind="primary"],
[data-testid="stMain"] .stButton > button[data-testid="baseButton-primary"] { color:#fff !important; }
/* Strong, consistent Image Studio visual system */
:root { color-scheme: light !important; }
.stApp, [data-testid="stAppViewContainer"] { background: #f3f5fc !important; }
[data-testid="stMainBlockContainer"] { max-width: 1680px; padding-left: 1.25rem; padding-right: 1.25rem; }
/* Card-like containers and expanders */
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
  background: #ffffff; border: 1px solid #e4e8f5; border-radius: 17px;
  box-shadow: 0 5px 18px rgba(31,43,79,.045); padding: 2px;
}
[data-testid="stMain"] [data-testid="stExpander"] {
  background: #ffffff !important; border: 1px solid #e2e5f2 !important;
  border-radius: 15px !important; box-shadow: 0 4px 15px rgba(31,43,79,.035);
}
/* Primary action buttons: always purple with white readable text */
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[data-testid="baseButton-primary"] {
  background: linear-gradient(110deg,#8957ff 0%,#6239ed 100%) !important;
  color: #ffffff !important; border: 0 !important; border-radius: 11px !important;
  min-height: 44px; font-weight: 700 !important;
  box-shadow: 0 5px 14px rgba(104,75,235,.22) !important;
}
[data-testid="stMain"] button[kind="primary"] *,
[data-testid="stMain"] button[data-testid="baseButton-primary"] * { color: #ffffff !important; fill: #ffffff !important; }
/* Secondary buttons: pale lavender background and deep-purple text */
[data-testid="stMain"] button[kind="secondary"],
[data-testid="stMain"] button[data-testid="baseButton-secondary"] {
  background: #f0ebff !important; color: #4e35bd !important;
  border: 1px solid #ddd3ff !important; border-radius: 11px !important;
  min-height: 42px; font-weight: 650 !important;
}
[data-testid="stMain"] button[kind="secondary"] *,
[data-testid="stMain"] button[data-testid="baseButton-secondary"] * { color: #4e35bd !important; fill: #4e35bd !important; }
[data-testid="stMain"] button:hover { border-color: #9b83ff !important; filter: brightness(.99); }
/* Sidebar retains the dark navy + vivid purple selection from the reference */
section[data-testid="stSidebar"] { background: #101831 !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #c5cde8 !important; }
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
  background: linear-gradient(110deg,#8957ff,#6239ed) !important;
  color: #fff !important; border-radius: 11px !important;
}
section[data-testid="stSidebar"] button[kind="primary"] *,
section[data-testid="stSidebar"] button[data-testid="baseButton-primary"] * { color: #fff !important; }
/* Inputs, upload area and slider accent */
[data-testid="stMain"] input, [data-testid="stMain"] textarea {
  background: #ffffff !important; color: #17213b !important; border-radius: 10px !important;
}
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] {
  background: #fbfaff !important; border: 1.5px dashed #b9aaff !important; border-radius: 14px !important;
}
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] * { color: #263451 !important; }
[data-testid="stMain"] [data-testid="stSlider"] [role="slider"] { background: #7448f5 !important; border-color: #7448f5 !important; }
[data-testid="stMain"] [data-testid="stMetric"] { background: #fff !important; border: 1px solid #e4e8f5; border-radius: 14px; }
header[data-testid="stHeader"] { background: rgba(244,246,252,.98) !important; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "Image Enhancement"

if "main_image" not in st.session_state:
    st.session_state.main_image = None

if "result_image" not in st.session_state:
    st.session_state.result_image = None

if "result_name" not in st.session_state:
    st.session_state.result_name = ""

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
        st.error("This image could not be opened. Please upload a valid PNG or JPG.")
        return None


def png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def fit_image(image, size):
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def make_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def add_text(image, text, position, color, size):
    out = image.convert("RGBA").copy()
    draw = ImageDraw.Draw(out)
    font = make_font(size)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = max(8, (out.width - tw) // 2)
    if position == "Top":
        y = 15
    elif position == "Center":
        y = (out.height - th) // 2
    else:
        y = max(8, out.height - th - 25)
    draw.text(
        (x, y), text, font=font, fill=color,
        stroke_width=max(1, size // 18), stroke_fill=(0, 0, 0, 170)
    )
    return out.convert("RGB")


@st.cache_resource
def get_background_session():
    """Load a portrait-focused segmentation model once per app process."""
    from rembg import new_session

    # BirefNet portrait is generally better for people, hair, and clothing edges
    # than the older general-purpose U2Net model.
    return new_session("birefnet-portrait")


def remove_background(image):
    """Return an RGBA person cutout with a refined transparent background."""
    from rembg import remove

    rgba = image.convert("RGBA")
    session = get_background_session()

    # Alpha matting can improve edge transitions around hair and clothing.
    # If matting fails for an image, fall back to the model's standard mask.
    try:
        result = remove(
            rgba,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
        )
    except Exception:
        result = remove(rgba, session=session)

    if not isinstance(result, Image.Image):
        result = Image.open(io.BytesIO(result))

    result = result.convert("RGBA")

    # Keep the model's alpha channel; do not flatten the cutout onto a color.
    # Slightly soften only the alpha edge to reduce jagged cutout outlines.
    alpha = result.getchannel("A")
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.4))
    result.putalpha(alpha)
    return result


def make_photo_sheet(image, photo_w_mm, photo_h_mm, copies, paper, dpi=300):
    # Output pixels at the chosen print resolution.
    mm_to_px = dpi / 25.4
    page_mm = (210, 297) if paper == "A4" else (216, 279)
    W, H = [round(v * mm_to_px) for v in page_mm]
    fw = max(1, round(photo_w_mm * mm_to_px))
    fh = max(1, round(photo_h_mm * mm_to_px))
    gap = round(3 * mm_to_px)
    margin = round(5 * mm_to_px)

    cols = max(1, (W - 2 * margin + gap) // (fw + gap))
    rows = max(1, (H - 2 * margin + gap) // (fh + gap))
    capacity = cols * rows

    sheet = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(sheet)
    thumb = fit_image(image, (fw, fh))
    count = min(copies, capacity)

    for i in range(count):
        x = margin + (i % cols) * (fw + gap)
        y = margin + (i // cols) * (fh + gap)
        sheet.paste(thumb, (x, y))
        draw.rectangle((x, y, x + fw - 1, y + fh - 1), outline="#bbbbbb", width=2)

    return sheet, count, capacity


def similarity_score(image_a, image_b):
    # Pixel similarity after resizing both images to the same dimensions.
    size = (160, 160)
    a = np.asarray(fit_image(image_a, size), dtype=np.float32)
    b = np.asarray(fit_image(image_b, size), dtype=np.float32)
    mae = np.mean(np.abs(a - b))
    return max(0.0, 100.0 * (1.0 - mae / 255.0))


def sketch_image(image, strength):
    gray = ImageOps.grayscale(image)
    inverted = ImageOps.invert(gray)
    blurred = inverted.filter(
        ImageFilter.GaussianBlur(radius=float(strength))
    )
    a = np.asarray(gray, dtype=np.float32)
    b = np.asarray(blurred, dtype=np.float32)
    dodge = np.minimum(255, a * 255 / np.maximum(1, 255 - b))
    return Image.fromarray(np.uint8(dodge.clip(0, 255))).convert("RGB")


def render_preview(original, result):
    left, right = st.columns(2)
    with left:
        st.markdown("**Original**")
        st.image(original, use_container_width=True)
    with right:
        st.markdown("**Edited result**")
        st.image(result, use_container_width=True)


def save_result(image, filename="image-studio.png"):
    st.session_state.result_image = image.copy()
    st.session_state.result_name = filename


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='padding:10px 6px 22px'>"
        "<div style='font-size:12px;color:#9ca9ce;letter-spacing:2px'>CREATIVE WORKSPACE</div>"
        "<div style='font-size:27px;font-weight:800;margin-top:5px'>✦ Image Studio</div>"
        "<div style='color:#9ca9ce;font-size:12px;margin-top:5px'>Your photos, your creativity.</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("##### IMAGE TOOLS")
    for number, name, description in TOOLS:
        is_selected = st.session_state.selected_tool == name
        if st.button(
            f"{number}   {name}",
            key=f"nav_{number}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.selected_tool = name
            st.session_state.result_image = None
            st.rerun()

    st.divider()
    st.caption("IMAGE STUDIO · BROWSER EDITION")
    st.caption("Upload • Edit • Export")


# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
tool_name = st.session_state.selected_tool
description = next(t[2] for t in TOOLS if t[1] == tool_name)

st.markdown(
    f"""
    <div class="hero">
      <span class="tool-chip">IMAGE STUDIO · TOOL {next(t[0] for t in TOOLS if t[1] == tool_name)}</span>
      <h1>{tool_name}</h1>
      <p>{description}</p>
      <p style="font-size:.82rem;color:#7b83a0;margin-top:13px">Upload&nbsp; · &nbsp;Customize&nbsp; · &nbsp;Preview&nbsp; · &nbsp;Export</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# WORKSPACE LAYOUT
# ---------------------------------------------------------
if tool_name == "Image Enhancement":
    upload_col, crop_col, settings_col = st.columns([1.02, 1.25, 1.08], gap="medium")

    with upload_col:
        with st.container(border=True):
            st.markdown("### 🟣 ① Upload your image")
            st.caption("Start with a clear JPG, PNG or WEBP photo.")
            uploaded = st.file_uploader(
                "Drag and drop your image or browse",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"upload_{tool_name}",
                help="Supported formats: JPG, PNG, WEBP",
            )
            original = load_image(uploaded)
            if original is None:
                st.markdown(
                    "<div style='text-align:center;padding:22px 8px;color:#737d98'>"
                    "<div style='font-size:42px;color:#7950f2'>☁</div>"
                    "<b>Choose an image to begin</b><br>"
                    "<span style='font-size:12px'>Your photo preview will appear below.</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.image(original, caption=f"Original · {original.width} × {original.height}px", use_container_width=True)

    with crop_col:
        with st.container(border=True):
            st.markdown("### 🟣 ② Crop & framing")
            st.caption("Optional. Keep Original to preserve the full photo.")
            crop_mode = st.selectbox(
                "Choose aspect ratio",
                ["Original", "Square (1:1)", "Portrait (4:5)", "Portrait (3:4)", "Landscape (16:9)", "Phone wallpaper (9:16)", "Custom margins"],
                key=f"crop_mode_{tool_name}",
            )
            if crop_mode == "Custom margins":
                c1, c2 = st.columns(2)
                with c1:
                    crop_left = st.slider("Left (%)", 0, 45, 0, key=f"crop_left_{tool_name}")
                    crop_top = st.slider("Top (%)", 0, 45, 0, key=f"crop_top_{tool_name}")
                with c2:
                    crop_right = st.slider("Right (%)", 0, 45, 0, key=f"crop_right_{tool_name}")
                    crop_bottom = st.slider("Bottom (%)", 0, 45, 0, key=f"crop_bottom_{tool_name}")
                if original is not None:
                    l = int(original.width * crop_left / 100)
                    t = int(original.height * crop_top / 100)
                    r = original.width - int(original.width * crop_right / 100)
                    b = original.height - int(original.height * crop_bottom / 100)
                    if r - l >= 10 and b - t >= 10:
                        original = original.crop((l, t, r, b))
                    else:
                        st.warning("Crop is too small. Reduce the margins.")
            elif original is not None and crop_mode != "Original":
                ratios = {
                    "Square (1:1)": (1, 1), "Portrait (4:5)": (4, 5),
                    "Portrait (3:4)": (3, 4), "Landscape (16:9)": (16, 9),
                    "Phone wallpaper (9:16)": (9, 16),
                }
                tw, th = ratios[crop_mode]
                ratio = tw / th
                if original.width / original.height > ratio:
                    nw = max(1, int(original.height * ratio))
                    x = (original.width - nw) // 2
                    original = original.crop((x, 0, x + nw, original.height))
                else:
                    nh = max(1, int(original.width / ratio))
                    y = (original.height - nh) // 2
                    original = original.crop((0, y, original.width, y + nh))
            if original is not None:
                st.caption(f"Working size: {original.width} × {original.height}px")
                st.image(original, use_container_width=True)

    with settings_col:
        with st.container(border=True):
            st.markdown("### 🟣 ③ Enhancement settings")
            st.caption("Adjust the image to get the best result.")
            brightness = st.slider("Brightness", -100, 100, 0, 5, key="enh_brightness")
            contrast = st.slider("Contrast", -100, 100, 0, 5, key="enh_contrast")
            saturation = st.slider("Saturation", -100, 100, 0, 5, key="enh_saturation")
            color = st.slider("Color intensity", -100, 100, 0, 5, key="enh_color")
            sharpness = st.slider("Sharpness", -100, 100, 0, 5, key="enh_sharpness")
            apply = st.button("✦ Apply Enhancement", type="primary", use_container_width=True)

    if original is not None:
        result = ImageEnhance.Brightness(original).enhance(max(0, 1 + brightness / 100))
        result = ImageEnhance.Contrast(result).enhance(max(0, 1 + contrast / 100))
        result = ImageEnhance.Color(result).enhance(max(0, 1 + saturation / 100))
        result = ImageEnhance.Color(result).enhance(max(0, 1 + color / 100))
        result = ImageEnhance.Sharpness(result).enhance(max(0, 1 + sharpness / 100))
        st.markdown(" ")
        preview_col, actions_col = st.columns([2.1, 1], gap="medium")
        with preview_col:
            with st.container(border=True):
                st.markdown("### Original image & enhanced preview")
                p1, p2 = st.columns(2, gap="medium")
                with p1:
                    st.markdown("**Original Image**")
                    st.image(original, use_container_width=True)
                with p2:
                    st.markdown("**Enhanced Preview**")
                    st.image(result, use_container_width=True)
        with actions_col:
            with st.container(border=True):
                st.markdown("### Download & actions")
                st.caption("Save your result or start again.")
                if apply:
                    save_result(result, "enhanced-image.png")
                    st.success("Enhancement applied.")
                if st.session_state.result_image is not None:
                    st.download_button(
                        "⬇ Download Image", data=png_bytes(st.session_state.result_image),
                        file_name=st.session_state.result_name or "enhanced-image.png",
                        mime="image/png", type="primary", use_container_width=True,
                    )
                else:
                    st.button("⬇ Download Image", disabled=True, use_container_width=True)
                a1, a2 = st.columns(2)
                with a1:
                    if st.button("↻ Reset All", use_container_width=True):
                        for key in ["enh_brightness", "enh_contrast", "enh_saturation", "enh_color", "enh_sharpness"]:
                            st.session_state[key] = 0
                        st.session_state.result_image = None
                        st.rerun()
                with a2:
                    if st.button("Use Original", use_container_width=True):
                        save_result(original, "original-image.png")
                        st.rerun()
                st.markdown(
                    "<div style='background:#f0f3ff;border-radius:12px;padding:13px;color:#35415f'>"
                    "<b>💡 Tips</b><br><small>• Increase contrast for clearer details.<br>"
                    "• Boost saturation for vivid colors.<br>• Increase sharpness for crisper images.</small></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("Upload an image to start enhancing it.")
else:
    with st.container(border=True):
        st.markdown("### ① Upload your image")
        st.caption("Start with a clear JPG, PNG or WEBP photo. You can crop it below before editing.")
        uploaded = st.file_uploader(
            "Choose a JPG, JPEG, PNG or WEBP image",
            type=["jpg", "jpeg", "png", "webp"],
            key=f"upload_{tool_name}",
        )
    original = load_image(uploaded)
    if original is not None:
        with st.expander("✂️ Optional crop & framing", expanded=False):
            st.caption("Crop the uploaded photo before using the selected tool.")
            crop_mode = st.selectbox(
                "Crop shape",
                ["Original", "Square (1:1)", "Portrait (4:5)", "Portrait (3:4)", "Landscape (16:9)", "Phone wallpaper (9:16)", "Custom margins"],
                key=f"crop_mode_{tool_name}",
            )
            if crop_mode == "Custom margins":
                c1, c2 = st.columns(2)
                with c1:
                    crop_left = st.slider("Crop left (%)", 0, 45, 0, key=f"crop_left_{tool_name}")
                    crop_top = st.slider("Crop top (%)", 0, 45, 0, key=f"crop_top_{tool_name}")
                with c2:
                    crop_right = st.slider("Crop right (%)", 0, 45, 0, key=f"crop_right_{tool_name}")
                    crop_bottom = st.slider("Crop bottom (%)", 0, 45, 0, key=f"crop_bottom_{tool_name}")
                l = int(original.width * crop_left / 100)
                t = int(original.height * crop_top / 100)
                r = original.width - int(original.width * crop_right / 100)
                b = original.height - int(original.height * crop_bottom / 100)
                if r - l >= 10 and b - t >= 10:
                    original = original.crop((l, t, r, b))
                else:
                    st.warning("Crop is too small. Reduce the crop margins.")
            elif crop_mode != "Original":
                ratios = {"Square (1:1)": (1, 1), "Portrait (4:5)": (4, 5),
                          "Portrait (3:4)": (3, 4), "Landscape (16:9)": (16, 9),
                          "Phone wallpaper (9:16)": (9, 16)}
                tw, th = ratios[crop_mode]
                ratio = tw / th
                if original.width / original.height > ratio:
                    nw = max(1, int(original.height * ratio))
                    x = (original.width - nw) // 2
                    original = original.crop((x, 0, x + nw, original.height))
                else:
                    nh = max(1, int(original.width / ratio))
                    y = (original.height - nh) // 2
                    original = original.crop((0, y, original.width, y + nh))
            st.caption(f"Working image size: {original.width} × {original.height} px")
            st.image(original, caption="Crop preview", use_container_width=True)

# ---------------------------------------------------------
# TOOL 2: IMAGE BLENDING
# ---------------------------------------------------------
if tool_name == "Image Blending":
    second_upload = st.file_uploader(
        "Upload the second image to blend",
        type=["jpg", "jpeg", "png", "webp"],
        key="blend_second",
    )
    opacity = st.slider("Overlay opacity", 0, 100, 50)
    mode = st.selectbox(
        "Blend mode",
        ["Normal", "Multiply", "Screen", "Difference", "Darken", "Lighten"],
    )

    if original and second_upload:
        second = load_image(second_upload)
        if second:
            base = original.convert("RGBA")
            overlay = fit_image(second, original.size).convert("RGBA")
            overlay.putalpha(round(opacity * 255 / 100))

            if mode == "Normal":
                result = Image.alpha_composite(base, overlay)
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
                result = Image.blend(base, blended, opacity / 100)

            result = result.convert("RGB")
            render_preview(original, result)
            if st.button("Apply blend", type="primary"):
                save_result(result, "blended-image.png")
                st.success("Blend created.")
    else:
        st.info("Upload both images to preview the blend.")

# ---------------------------------------------------------
# TOOL 3: AI BACKGROUND CHANGE
# ---------------------------------------------------------
elif tool_name == "AI Background Change":
    background_upload = st.file_uploader(
        "Optional: upload a replacement background image",
        type=["jpg", "jpeg", "png", "webp"],
        key="replacement_background",
    )
    bg_color = st.color_picker("Or choose a background color", "#dce5f5")
    scale = st.slider("Subject scale", 50, 150, 100)

    if original:
        if st.button("Remove background and replace", type="primary"):
            try:
                with st.spinner(
                    "Removing the background. The first run may download the portrait AI model..."
                ):
                    cutout = remove_background(original)

                    if background_upload is not None:
                        bg = load_image(background_upload)
                        if bg is None:
                            st.error("The replacement background image could not be opened.")
                            st.stop()
                        canvas = fit_image(bg, original.size).convert("RGBA")
                    else:
                        rgb = tuple(
                            int(bg_color[i:i + 2], 16) for i in (1, 3, 5)
                        )
                        canvas = Image.new("RGBA", original.size, rgb + (255,))

                    # Resize the subject if requested, then center it on a
                    # transparent canvas the same size as the background.
                    subject = cutout
                    if scale != 100:
                        new_size = (
                            max(1, round(subject.width * scale / 100)),
                            max(1, round(subject.height * scale / 100)),
                        )
                        subject = subject.resize(
                            new_size, Image.Resampling.LANCZOS
                        )

                    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                    x = (canvas.width - subject.width) // 2
                    y = (canvas.height - subject.height) // 2

                    # Crop safely when the scaled subject is larger than the canvas.
                    left = max(0, x)
                    top = max(0, y)
                    right = min(canvas.width, x + subject.width)
                    bottom = min(canvas.height, y + subject.height)

                    if right > left and bottom > top:
                        crop = subject.crop((
                            left - x,
                            top - y,
                            right - x,
                            bottom - y,
                        ))
                        layer.alpha_composite(crop, (left, top))

                    result = Image.alpha_composite(canvas, layer).convert("RGB")
                    st.image(
                        result,
                        caption="Background replaced",
                        use_container_width=True,
                    )
                    save_result(result, "background-changed.png")
                    st.success("Background replacement completed.")

            except ImportError as exc:
                st.error(
                    "Background-removal packages are missing. Check requirements.txt "
                    "contains rembg and onnxruntime, then reboot the app."
                )
                st.caption(f"Technical detail: {exc}")
            except Exception as exc:
                st.error(f"Background removal failed: {type(exc).__name__}: {exc}")
                st.info(
                    "If this is the first run, check the deployment logs for model "
                    "download errors or memory limits. After changing requirements.txt, "
                    "reboot the app."
                )
    else:
        st.info("Upload a subject photo to replace its background.")

# ---------------------------------------------------------
# TOOL 4: BLACK & WHITE
# ---------------------------------------------------------
elif tool_name == "Black & White":
    contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.05)
    if original:
        result = ImageOps.grayscale(original).convert("RGB")
        result = ImageEnhance.Contrast(result).enhance(contrast)
        render_preview(original, result)
        if st.button("Apply black & white", type="primary"):
            save_result(result, "black-and-white.png")
    else:
        st.info("Upload a photo to convert it to black and white.")

# ---------------------------------------------------------
# TOOL 5: COLOR TO SKETCH
# ---------------------------------------------------------
elif tool_name == "Color to Sketch":
    strength = st.slider("Sketch blur strength", 1, 15, 5)
    if original:
        result = sketch_image(original, strength)
        render_preview(original, result)
        if st.button("Apply sketch effect", type="primary"):
            save_result(result, "pencil-sketch.png")
    else:
        st.info("Upload a photo to create a pencil-style sketch.")

# ---------------------------------------------------------
# TOOL 6 & 7: PRINT PHOTO SHEETS
# ---------------------------------------------------------
elif tool_name in ["Passport Photo Sheet", "Stamp Photo Maker"]:
    is_passport = tool_name == "Passport Photo Sheet"
    default_w, default_h = (35, 45) if is_passport else (25, 30)

    c1, c2, c3 = st.columns(3)
    with c1:
        photo_w = st.number_input("Width (mm)", 5, 100, default_w)
    with c2:
        photo_h = st.number_input("Height (mm)", 5, 100, default_h)
    with c3:
        copies = st.number_input("Number of copies", 1, 100, 8)

    paper = st.selectbox("Paper size", ["A4", "Letter"])
    dpi = st.selectbox("Print resolution (DPI)", [150, 300], index=1)

    if original:
        if st.button("Create printable sheet", type="primary"):
            sheet, placed, capacity = make_photo_sheet(
                original, photo_w, photo_h, int(copies), paper, dpi
            )
            st.image(sheet, caption=f"Printable sheet — {placed} photos", use_container_width=True)
            save_result(sheet, "photo-sheet.png")
            if placed < copies:
                st.warning(
                    f"Only {placed} copies fit on this paper at the selected dimensions. "
                    f"Maximum capacity: {capacity}."
                )
    else:
        st.info("Upload the photo you want to print.")

# ---------------------------------------------------------
# TOOL 8: IMAGE SIMILARITY
# ---------------------------------------------------------
elif tool_name == "Image Similarity":
    second_upload = st.file_uploader(
        "Upload the second image",
        type=["jpg", "jpeg", "png", "webp"],
        key="similarity_second",
    )

    if original and second_upload:
        second = load_image(second_upload)
        if second:
            score = similarity_score(original, second)
            col1, col2 = st.columns(2)
            with col1:
                st.image(original, caption="Image A", use_container_width=True)
            with col2:
                st.image(second, caption="Image B", use_container_width=True)
            st.metric("Pixel similarity estimate", f"{score:.1f}%")

            a = np.asarray(fit_image(original, (400, 400)), dtype=np.int16)
            b = np.asarray(fit_image(second, (400, 400)), dtype=np.int16)
            diff = Image.fromarray(
                np.uint8(np.abs(a - b).mean(axis=2).clip(0, 255))
            )
            st.image(diff, caption="Difference map", use_container_width=True)
            st.caption("This is a pixel-based comparison, not a semantic AI similarity score.")
    else:
        st.info("Upload two images to compare them.")

# ---------------------------------------------------------
# TOOL 9: ADD DATE AND TEXT
# ---------------------------------------------------------
elif tool_name == "Add Date & Text":
    text = st.text_input("Caption or watermark", "Your caption")
    add_date = st.checkbox("Add date", value=False)
    chosen_date = st.date_input("Date", value=date.today(), disabled=not add_date)
    position = st.selectbox("Text position", ["Bottom", "Top", "Center"])
    size = st.slider("Font size", 12, 100, 36)
    color = st.color_picker("Text color", "#FFFFFF")

    if original:
        combined = text
        if add_date:
            combined = f"{text}  {chosen_date.isoformat()}".strip()
        result = add_text(original, combined, position, color, size)
        render_preview(original, result)
        if st.button("Apply text overlay", type="primary"):
            save_result(result, "text-overlay.png")
    else:
        st.info("Upload a photo to add text or a date.")

# ---------------------------------------------------------
# TOOL 10: VISIBLE GEOTAGGING
# ---------------------------------------------------------
elif tool_name == "Image Geotagging":
    location = st.text_input("Location", "Bengaluru, India")
    coords = st.text_input("GPS coordinates (optional)", "")
    tag_date = st.date_input("Date", value=date.today())
    position = st.selectbox("Overlay position", ["Bottom", "Top", "Center"])

    if original:
        lines = [x.strip() for x in [location, coords, tag_date.isoformat()] if x.strip()]
        result = original.copy()
        y = 18 if position == "Top" else (
            max(10, result.height // 2) if position == "Center" else max(10, result.height - 120)
        )
        draw = ImageDraw.Draw(result)
        font = make_font(max(16, result.width // 35))
        padding = max(8, result.width // 80)
        line_height = max(22, result.width // 30)
        box_height = len(lines) * line_height + 2 * padding
        draw.rectangle(
            (0, max(0, y - padding), result.width, min(result.height, y + box_height)),
            fill=(0, 0, 0),
        )
        for i, line in enumerate(lines):
            draw.text((padding, y + i * line_height), line, fill="white", font=font)

        render_preview(original, result)
        if st.button("Apply location overlay", type="primary"):
            save_result(result, "geotag-overlay.png")
            st.success("Visible location overlay created.")
        st.caption(
            "This adds visible text to the image. It does not write GPS coordinates into EXIF metadata."
        )
    else:
        st.info("Upload a photo to add a location overlay.")

# ---------------------------------------------------------
# TOOL 11: COLLAGE MAKER
# ---------------------------------------------------------
elif tool_name == "Collage Maker":
    extra_uploads = st.file_uploader(
        "Upload photos for your collage",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="collage_images",
    )
    columns = st.selectbox("Grid columns", [2, 3, 4], index=1)
    gap = st.slider("Spacing", 0, 40, 12)
    cell_size = st.selectbox("Cell size", [250, 400, 600], index=1)
    title = st.text_input("Optional collage title", "")

    if original or extra_uploads:
        images = []
        if original:
            images.append(original)
        for f in extra_uploads or []:
            img = load_image(f)
            if img is not None:
                images.append(img)

        if images:
            cols = int(columns)
            rows = math.ceil(len(images) / cols)
            width = cols * cell_size + (cols + 1) * gap
            height = rows * cell_size + (rows + 1) * gap
            title_h = 70 if title else 0
            collage = Image.new("RGB", (width, height + title_h), "white")
            draw = ImageDraw.Draw(collage)

            if title:
                draw.text(
                    (gap, 12), title, fill="#222222",
                    font=make_font(max(20, cell_size // 12))
                )

            for i, img in enumerate(images):
                x = gap + (i % cols) * (cell_size + gap)
                y = title_h + gap + (i // cols) * (cell_size + gap)
                collage.paste(fit_image(img, (cell_size, cell_size)), (x, y))

            st.image(collage, caption=f"Collage preview · {len(images)} images", use_container_width=True)
            if st.button("Export collage", type="primary"):
                save_result(collage, "collage.png")
    else:
        st.info("Upload a main image and any additional photos.")

# ---------------------------------------------------------
# TOOL 12: WALLPAPER DESIGNER
# ---------------------------------------------------------
elif tool_name == "Wallpaper Designer":
    preset = st.selectbox(
        "Canvas preset",
        ["Phone (1080 × 1920)", "Desktop (1920 × 1080)", "Square (1080 × 1080)"],
    )
    bg = st.color_picker("Background color", "#25234D")
    title = st.text_input("Wallpaper title", "DREAM BIG")
    title_color = st.color_picker("Title color", "#FFFFFF")
    title_position = st.selectbox("Title position", ["Top", "Center", "Bottom"])

    dimensions = {
        "Phone (1080 × 1920)": (1080, 1920),
        "Desktop (1920 × 1080)": (1920, 1080),
        "Square (1080 × 1080)": (1080, 1080),
    }

    if st.button("Generate wallpaper", type="primary"):
        size = dimensions[preset]
        rgb = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
        wallpaper = Image.new("RGB", size, rgb)

        if original:
            photo = fit_image(original, (int(size[0] * .84), int(size[1] * .68)))
            wallpaper.paste(photo, ((size[0] - photo.width) // 2, int(size[1] * .08)))

        wallpaper = add_text(
            wallpaper, title, title_position, title_color,
            max(28, size[0] // 15)
        )
        st.image(wallpaper, caption="Wallpaper preview", use_container_width=True)
        save_result(wallpaper, "wallpaper.png")

# ---------------------------------------------------------
# SHARED DOWNLOAD
# ---------------------------------------------------------
st.divider()
st.markdown("### Export your image")

if st.session_state.result_image is not None:
    st.download_button(
        "⬇ Download edited image (PNG)",
        data=png_bytes(st.session_state.result_image),
        file_name=st.session_state.result_name or "image-studio.png",
        mime="image/png",
        type="primary",
        use_container_width=True,
    )
else:
    st.caption("Complete an edit or generate a design to enable downloading.")
