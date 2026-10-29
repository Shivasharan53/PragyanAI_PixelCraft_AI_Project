# PragyanAI Image Studio — Streamlit edition

A modular Streamlit image studio with 12 tools:

1. Image enhancement
2. Image blending
3. AI background removal and replacement
4. Color to black and white
5. Color to pencil sketch / line art
6. Passport photo sheets
7. Stamp-size photo sheets
8. Image similarity comparison
9. Add date, birthday wishes, titles, and captions
10. Add visible geotags and optional GPS EXIF metadata
11. Multi-image collage and thumbnail creation
12. Wallpaper and title design

## Run locally

Python 3.10–3.12 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

If you don't need AI background removal immediately, install `requirements-minimal.txt` instead. The background tool will tell you that `rembg` is missing if you try to use it. `rembg` may download its model on first use and can make cloud deployments significantly larger.

## Deploy on Streamlit Community Cloud

1. Push this project folder to a GitHub repository.
2. Open Streamlit Community Cloud and create an app from that repository.
3. Set the main file path to `app.py`.
4. Choose a Python version compatible with the dependencies.
5. Deploy.

For a lightweight cloud deployment, use `requirements-minimal.txt` renamed to `requirements.txt`, then add `rembg[cpu]` only if your deployment resources support it. Test background removal after deployment.

## Project structure

```text
PragyanAI_Image_Studio/
├── app.py
├── requirements.txt
├── requirements-minimal.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── image_studio/
    ├── __init__.py
    ├── io_utils.py
    ├── editing.py
    ├── print_layout.py
    ├── analysis.py
    ├── design.py
    └── metadata.py
```

## Notes

- Images are processed in memory by the Streamlit app; this project does not upload images to a separate database.
- For passport/stamp layouts, dimensions are configurable. Confirm the applicable official photo specifications for your use case.
- Print sheets are generated at the selected DPI. When printing the PDF, choose **Actual Size / 100%**, not “Fit to page.”
- Similarity is a heuristic based on perceptual hashing and a structural comparison. It is not a face-recognition system or proof of identity.
- GPS metadata can expose a sensitive location. Only embed coordinates you intend to share.
- AI background replacement is automated; hair, transparent objects, and complex edges may require manual retouching in a future iteration.
