import streamlit as st
from PIL import Image, ImageOps, ImageEnhance

from image_studio.editing import (
    enhance_image,
    blend_images,
    grayscale_image,
    sketch_image,
    remove_image_background,
    replace_background,
)

st.set_page_config(
    page_title="PragyanAI Image Studio",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 PragyanAI Image Studio")
st.write("Your all-in-one image editing studio.")

tool = st.sidebar.selectbox(
    "Choose a tool",
    [
        "Image Enhancement",
        "Image Blending",
        "AI Background Change",
        "Color to Black and White",
        "Color to Sketch",
    ],
)

def upload_image(label, key):
    file = st.file_uploader(
        label,
        type=["png", "jpg", "jpeg", "webp"],
        key=key,
    )
    if file is None:
        return None

    try:
        with Image.open(file) as img:
            img.load()
            return ImageOps.exif_transpose(img).copy()
    except Exception as exc:
        st.error(f"Could not open image: {exc}")
        return None


def show_result(image, filename="edited_image.png"):
    st.image(image, caption="Preview", use_container_width=True)

    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGBA")
        image_format = "PNG"
    else:
        image_format = "PNG"

    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format=image_format)

    st.download_button(
        "⬇️ Download image",
        data=buffer.getvalue(),
        file_name=filename,
        mime="image/png",
    )


if tool == "Image Enhancement":
    st.subheader("✨ Image Enhancement")
    image = upload_image("Upload an image", "enhance")

    if image:
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Original", use_container_width=True)
        with col2:
            brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.05)
            contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.05)
            color = st.slider("Color", 0.0, 2.0, 1.0, 0.05)
            sharpness = st.slider("Sharpness", 0.0, 3.0, 1.0, 0.05)

        if st.button("Enhance image", type="primary"):
            result = enhance_image(
                image,
                brightness=brightness,
                contrast=contrast,
                color=color,
                sharpness=sharpness,
            )
            st.subheader("Enhanced result")
            show_result(result, "enhanced.png")


elif tool == "Image Blending":
    st.subheader("🖼️ Image Blending")
    col1, col2 = st.columns(2)

    with col1:
        base = upload_image("Upload base image", "blend_base")
    with col2:
        overlay = upload_image("Upload overlay image", "blend_overlay")

    if base and overlay:
        opacity = st.slider("Overlay opacity", 0.0, 1.0, 0.5, 0.05)
        mode = st.selectbox(
            "Blend mode", ["Normal", "Multiply", "Screen", "Add"]
        )
        fit = st.selectbox(
            "Overlay fit", ["Cover/crop to base", "Stretch", "Contain"]
        )

        if st.button("Blend images", type="primary"):
            result = blend_images(base, overlay, opacity, mode, fit)
            show_result(result, "blended.png")


elif tool == "AI Background Change":
    st.subheader("🌄 AI Background Change")
    st.info(
        "Upload a subject photo and a replacement background. "
        "The first AI model initialization may take some time."
    )

    col1, col2 = st.columns(2)
    with col1:
        subject = upload_image("Upload person or subject", "subject")
    with col2:
        background = upload_image("Upload new background", "background")

    if subject:
        with st.expander("Preview subject"):
            st.image(subject, use_container_width=True)

    if subject and background:
        fit = st.selectbox("Background sizing", ["Cover/crop", "Stretch"])

        if st.button("Remove background and replace it", type="primary"):
            try:
                with st.spinner("Removing background with AI..."):
                    result = replace_background(subject, background, fit)

                st.success("Background replacement complete!")
                show_result(result, "background_replaced.png")

            except Exception as exc:
                st.error("Background replacement failed.")
                st.code(str(exc))
                st.info(
                    "If the model download or initialization failed, "
                    "check the Streamlit Cloud logs and dependencies."
                )


elif tool == "Color to Black and White":
    st.subheader("⚫ Color to Black and White")
    image = upload_image("Upload a color image", "grayscale")

    if image:
        contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.05)
        brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.05)

        if st.button("Convert to black and white", type="primary"):
            result = grayscale_image(
                image,
                contrast=contrast,
                brightness=brightness,
            )
            show_result(result, "black_and_white.png")


elif tool == "Color to Sketch":
    st.subheader("✏️ Color to Sketch")
    image = upload_image("Upload a photo", "sketch")

    if image:
        style = st.selectbox(
            "Sketch style", ["Pencil", "Charcoal", "Bold line art"]
        )
        strength = st.slider("Sketch strength", 3, 21, 9, 2)

        if st.button("Create sketch", type="primary"):
            result = sketch_image(image, style, strength)
            show_result(result, "sketch.png")


st.divider()
st.caption("PragyanAI Image Studio • Built with Streamlit and Python")
