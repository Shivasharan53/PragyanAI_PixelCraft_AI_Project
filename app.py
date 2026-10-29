import streamlit as st
from PIL import Image, ImageOps
from image_studio.io_utils import load_image, image_to_bytes, safe_filename
from image_studio.editing import enhance_image, blend_images, grayscale_image, sketch_image, replace_background
from image_studio.print_layout import make_photo_sheet, make_single_photo
from image_studio.analysis import compare_images
from image_studio.design import add_text_overlay, make_collage, make_wallpaper
from image_studio.metadata import add_geotag_overlay, embed_gps_metadata

st.set_page_config(page_title="PragyanAI Image Studio", page_icon="🖼️", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#172554,#4338ca,#0f766e); color:white;}
.small-muted {color: #64748b; font-size: .92rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🖼️ PragyanAI Image Studio</h1><p>12 practical tools for photo editing, print layouts, image analysis, and creative design.</p></div>', unsafe_allow_html=True)
st.write("Upload your own images, choose a tool, preview the result, and download it. Images are processed in this app session.")

TOOLS = [
    "Image enhancement", "Image blending", "AI background change", "Color to black & white",
    "Color to sketch", "Passport photo sheet", "Stamp-size photo", "Image similarity",
    "Add date & text", "Image geotag", "Collage & thumbnail maker", "Wallpaper & title designer"
]
tool = st.sidebar.selectbox("Choose a tool", TOOLS)
st.sidebar.markdown("---")
st.sidebar.caption("Tip: use high-resolution originals for print work. Passport and stamp dimensions are configurable; confirm local requirements before printing official photos.")

def upload_image(label, key, required=True):
    file = st.file_uploader(label, type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"], key=key)
    if file is None:
        return None
    try:
        return load_image(file.getvalue())
    except Exception as exc:
        st.error(f"Could not open image: {exc}")
        return None

def preview_download(image, filename="pragyanai_result.png", caption="Result"):
    if image is None:
        return
    st.image(image, caption=caption, use_container_width=True)
    st.download_button("⬇️ Download PNG", data=image_to_bytes(image, "PNG"), file_name=filename, mime="image/png", use_container_width=True)
    jpg = image_to_bytes(image.convert("RGB"), "JPEG")
    st.download_button("⬇️ Download JPG", data=jpg, file_name=safe_filename(filename.rsplit(".",1)[0]) + ".jpg", mime="image/jpeg", use_container_width=True)

def two_columns():
    return st.columns(2, gap="large")

if tool == "Image enhancement":
    image = upload_image("Upload image", "enhance_upload")
    if image:
        left, right = two_columns()
        with left:
            st.image(image, caption="Original", use_container_width=True)
            brightness = st.slider("Brightness", 0.25, 2.5, 1.0, 0.05)
            contrast = st.slider("Contrast", 0.25, 2.5, 1.0, 0.05)
            color = st.slider("Color saturation", 0.0, 2.5, 1.0, 0.05)
            sharpness = st.slider("Sharpness", 0.0, 3.0, 1.0, 0.05)
        result = enhance_image(image, brightness, contrast, color, sharpness)
        with right:
            preview_download(result, "enhanced_image.png", "Enhanced image")

elif tool == "Image blending":
    c1, c2 = st.columns(2)
    with c1: base = upload_image("Upload base image", "blend_base")
    with c2: overlay = upload_image("Upload overlay image", "blend_overlay")
    if base and overlay:
        opacity = st.slider("Overlay opacity", 0.0, 1.0, 0.5, 0.05)
        mode = st.selectbox("Blend mode", ["Normal", "Multiply", "Screen", "Add"])
        fit = st.selectbox("Overlay fit", ["Cover/crop to base", "Stretch to base", "Contain"])
        result = blend_images(base, overlay, opacity, mode, fit)
        a, b = two_columns()
        with a: st.image(base, caption="Base image", use_container_width=True)
        with b: preview_download(result, "blended_image.png", "Blended result")

elif tool == "AI background change":
    st.info("This tool uses `rembg` for foreground/background separation. First run may download a model. If the dependency or model is unavailable, the app will explain how to enable it.")
    c1, c2 = st.columns(2)
    with c1: subject = upload_image("Upload subject/person image", "bg_subject")
    with c2: background = upload_image("Upload replacement background (e.g. tower)", "bg_replacement")
    if subject and background:
        fit = st.selectbox("Background fit", ["Cover/crop", "Stretch"])
        if st.button("Remove old background and compose", type="primary"):
            with st.spinner("Removing background…"):
                try:
                    result = replace_background(subject, background, fit)
                    st.session_state["bg_result"] = result
                except Exception as exc:
                    st.error(str(exc))
        if st.session_state.get("bg_result") is not None:
            preview_download(st.session_state["bg_result"], "background_replaced.png", "New background")

elif tool == "Color to black & white":
    image = upload_image("Upload color image", "bw_upload")
    if image:
        strength = st.slider("Grayscale contrast", 0.5, 2.0, 1.0, 0.05)
        result = grayscale_image(image, strength)
        a, b = two_columns()
        with a: st.image(image, caption="Original", use_container_width=True)
        with b: preview_download(result, "black_and_white.png", "Black & white")

elif tool == "Color to sketch":
    image = upload_image("Upload image", "sketch_upload")
    if image:
        style = st.selectbox("Sketch style", ["Pencil", "Bold line art"])
        strength = st.slider("Detail / line strength", 1, 31, 9, 2)
        result = sketch_image(image, style, strength)
        a, b = two_columns()
        with a: st.image(image, caption="Original", use_container_width=True)
        with b: preview_download(result, "sketch.png", "Sketch result")

elif tool in ("Passport photo sheet", "Stamp-size photo"):
    image = upload_image("Upload portrait/photo", "print_upload")
    if image:
        st.image(image, caption="Uploaded photo", width=260)
        kind = "passport" if tool == "Passport photo sheet" else "stamp"
        default_w, default_h = (35.0, 45.0) if kind == "passport" else (25.0, 25.0)
        c1, c2, c3 = st.columns(3)
        with c1:
            width_mm = st.number_input("Photo width (mm)", min_value=10.0, max_value=100.0, value=default_w, step=1.0)
            height_mm = st.number_input("Photo height (mm)", min_value=10.0, max_value=120.0, value=default_h, step=1.0)
        with c2:
            copies = st.number_input("Copies", min_value=1, max_value=100, value=8 if kind=="passport" else 12, step=1)
            dpi = st.selectbox("Print resolution (DPI)", [150, 200, 300, 600], index=2)
        with c3:
            paper = st.selectbox("Paper size", ["A4", "Letter", "4x6 inch"])
            margin = st.number_input("Margin (mm)", min_value=0.0, max_value=20.0, value=5.0, step=1.0)
        if st.button("Create printable sheet", type="primary"):
            sheet, pdf = make_photo_sheet(image, int(copies), width_mm, height_mm, dpi, paper, margin)
            st.session_state["print_sheet"] = sheet
            st.session_state["print_pdf"] = pdf
        if st.session_state.get("print_sheet") is not None:
            st.image(st.session_state["print_sheet"], caption="Printable photo sheet", use_container_width=True)
            st.download_button("Download sheet PNG", image_to_bytes(st.session_state["print_sheet"], "PNG"), "photo_sheet.png", "image/png")
            st.download_button("Download print-ready PDF", st.session_state["print_pdf"], "photo_sheet.pdf", "application/pdf")
            st.caption("Print at 100% / Actual Size. Printer margins and paper scaling can affect final physical dimensions.")

elif tool == "Image similarity":
    c1, c2 = st.columns(2)
    with c1: img1 = upload_image("Upload first image", "similarity_1")
    with c2: img2 = upload_image("Upload second image", "similarity_2")
    if img1 and img2:
        score, hash_distance, structural = compare_images(img1, img2)
        st.metric("Overall similarity", f"{score:.1f}%")
        m1, m2 = st.columns(2)
        m1.metric("Perceptual hash distance", f"{hash_distance}/64", help="Lower means more similar.")
        m2.metric("Structural similarity (approx.)", f"{structural:.1f}%")
        a, b = two_columns()
        with a: st.image(img1, caption="Image 1", use_container_width=True)
        with b: st.image(img2, caption="Image 2", use_container_width=True)
        st.caption("Similarity is an estimate, not proof that two images are identical. Cropping, rotation, and heavy edits can change the score.")

elif tool == "Add date & text":
    image = upload_image("Upload image", "text_upload")
    if image:
        text = st.text_input("Text to add", "Happy Birthday!")
        date_text = st.text_input("Date (optional)", "")
        position = st.selectbox("Position", ["Bottom center", "Bottom left", "Bottom right", "Top left", "Top center", "Top right", "Center"])
        color = st.color_picker("Text color", "#FFFFFF")
        size = st.slider("Font size", 12, 120, max(24, image.width // 18))
        stroke = st.checkbox("Add dark outline for readability", True)
        result = add_text_overlay(image, text, date_text, position, color, size, stroke)
        a, b = two_columns()
        with a: st.image(image, caption="Original", use_container_width=True)
        with b: preview_download(result, "image_with_text.png", "Image with text/date")

elif tool == "Image geotag":
    image = upload_image("Upload image", "geo_upload")
    if image:
        place = st.text_input("Location name", "Bengaluru, India")
        latitude = st.text_input("Latitude (optional, for metadata)", "")
        longitude = st.text_input("Longitude (optional, for metadata)", "")
        date_text = st.text_input("Date/time to display (optional)", "")
        overlay = st.checkbox("Show location as visible text on image", True)
        if st.button("Add geotag", type="primary"):
            result = add_geotag_overlay(image, place, latitude, longitude, date_text) if overlay else image.copy()
            try:
                gps_bytes = embed_gps_metadata(result, latitude, longitude) if latitude.strip() and longitude.strip() else None
            except Exception as exc:
                st.warning(f"Could not embed GPS metadata: {exc}")
                gps_bytes = None
            st.session_state["geo_result"] = result
            st.session_state["geo_bytes"] = gps_bytes
        if st.session_state.get("geo_result") is not None:
            preview_download(st.session_state["geo_result"], "geotagged_image.png", "Geotagged image")
            if st.session_state.get("geo_bytes"):
                st.download_button("Download JPEG with GPS metadata", st.session_state["geo_bytes"], "geotagged_image.jpg", "image/jpeg")
            st.caption("Only add coordinates you have permission to share. PNG downloads display the overlay; GPS EXIF is included in the JPEG download when piexif is installed.")

elif tool == "Collage & thumbnail maker":
    files = st.file_uploader("Upload multiple images (selection order is used)", type=["png","jpg","jpeg","webp","bmp"], accept_multiple_files=True, key="collage_upload")
    if files:
        images = [load_image(f.getvalue()) for f in files]
        names = [f.name for f in files]
        st.write("Selected image order:")
        order_labels = st.multiselect("Reorder by selecting filenames in desired order", names, default=names)
        ordered = [images[names.index(n)] for n in order_labels if n in names]
        title = st.text_input("Title", "My Photo Story")
        layout = st.selectbox("Layout", ["Grid", "Horizontal strip", "Vertical strip"])
        columns = st.slider("Grid columns", 1, 5, 3)
        caption = st.checkbox("Add filenames as captions", True)
        size = st.selectbox("Output size", ["Thumbnail 1280×720", "Square 1080×1080", "Large 1920×1080"])
        dims = {"Thumbnail 1280×720": (1280,720), "Square 1080×1080": (1080,1080), "Large 1920×1080": (1920,1080)}[size]
        if st.button("Create collage / thumbnail", type="primary"):
            result = make_collage(ordered, [names[names.index(n)] for n in order_labels], title, layout, columns, caption, dims)
            st.session_state["collage_result"] = result
        if st.session_state.get("collage_result") is not None:
            preview_download(st.session_state["collage_result"], "collage_thumbnail.png", "Collage / thumbnail")

elif tool == "Wallpaper & title designer":
    files = st.file_uploader("Upload one or more images", type=["png","jpg","jpeg","webp","bmp"], accept_multiple_files=True, key="wallpaper_upload")
    if files:
        images = [load_image(f.getvalue()) for f in files]
        title = st.text_input("Wallpaper title", "Make Today Count")
        subtitle = st.text_input("Subtitle (optional)", "")
        device = st.selectbox("Target format", ["Desktop 1920×1080", "Laptop 1366×768", "Mobile 1080×1920", "Square 1080×1080"])
        dims = {"Desktop 1920×1080": (1920,1080), "Laptop 1366×768": (1366,768), "Mobile 1080×1920": (1080,1920), "Square 1080×1080": (1080,1080)}[device]
        mode = st.selectbox("Composition", ["Use first image", "Collage all images"])
        if st.button("Create wallpaper", type="primary"):
            result = make_wallpaper(images, title, subtitle, dims, mode)
            st.session_state["wallpaper_result"] = result
        if st.session_state.get("wallpaper_result") is not None:
            preview_download(st.session_state["wallpaper_result"], "wallpaper.png", "Wallpaper")

st.markdown("---")
st.caption("PragyanAI Image Studio • Local image processing in Python • Review generated results before printing or publishing.")
