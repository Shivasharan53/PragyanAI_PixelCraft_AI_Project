from io import BytesIO
from PIL import Image, ImageOps, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

MM_TO_INCH = 1 / 25.4

def make_single_photo(image, width_mm=35, height_mm=45, dpi=300):
    size = (max(1, round(width_mm * MM_TO_INCH * dpi)), max(1, round(height_mm * MM_TO_INCH * dpi)))
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))

def _paper_dimensions(name):
    if name == "Letter":
        return (215.9, 279.4)
    if name == "4x6 inch":
        return (101.6, 152.4)
    return (210, 297)

def make_photo_sheet(image, copies, width_mm, height_mm, dpi=300, paper="A4", margin_mm=5):
    paper_w_mm, paper_h_mm = _paper_dimensions(paper)
    page_w = round(paper_w_mm / 25.4 * dpi)
    page_h = round(paper_h_mm / 25.4 * dpi)
    photo = make_single_photo(image, width_mm, height_mm, dpi)
    margin = round(margin_mm / 25.4 * dpi)
    gap = max(round(2 / 25.4 * dpi), 1)
    cell_w, cell_h = photo.size
    cols = max(1, (page_w - 2*margin + gap) // (cell_w + gap))
    rows = max(1, (page_h - 2*margin + gap) // (cell_h + gap))
    capacity = cols * rows
    if copies > capacity:
        raise ValueError(f"{paper} at {dpi} DPI fits only {capacity} photos of this size. Reduce copies, margins, or photo size.")
    sheet = Image.new("RGB", (page_w, page_h), "white")
    draw = ImageDraw.Draw(sheet)
    for i in range(copies):
        row, col = divmod(i, cols)
        x = margin + col * (cell_w + gap)
        y = margin + row * (cell_h + gap)
        sheet.paste(photo, (x, y))
        draw.rectangle((x, y, x+cell_w-1, y+cell_h-1), outline=(190,190,190), width=max(1, dpi//300))
    png = BytesIO()
    sheet.save(png, format="PNG", optimize=True)
    pdf_buffer = BytesIO()
    page_w_pt, page_h_pt = paper_w_mm / 25.4 * 72, paper_h_mm / 25.4 * 72
    pdf = canvas.Canvas(pdf_buffer, pagesize=(page_w_pt, page_h_pt))
    pdf.drawImage(ImageReader(BytesIO(png.getvalue())), 0, 0, width=page_w_pt, height=page_h_pt, preserveAspectRatio=False, mask="auto")
    pdf.showPage()
    pdf.save()
    return sheet, pdf_buffer.getvalue()
