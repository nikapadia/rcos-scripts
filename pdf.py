import csv
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from textwrap import wrap
from reportlab.lib.utils import ImageReader

def create_pdf_from_csv(csv_file, pdf_file, footer_text=""):
    # Use landscape orientation
    page_width, page_height = landscape(letter)

    # Adjusted dimensions for closer quadrants
    quadrant_width = page_width / 2
    quadrant_height = page_height / 2.2  # Reduce the quadrant height to move rows closer
    vertical_gap = (page_height - (2 * quadrant_height)) / 2  # Equal spacing above and below

    number_font_size = 128
    name_font_size = 24
    name_line_spacing = 18  # Space between lines in the project name

    # Initialize PDF
    c = canvas.Canvas(pdf_file, pagesize=landscape(letter))

    def draw_footer(canvas, text):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawCentredString(page_width/2.0, 30, text)
        canvas.restoreState()

    # Load QR image if present
    qr_path = os.path.join(os.getcwd(), "qr.png")
    qr_image = None
    if os.path.exists(qr_path):
        try:
            qr_image = ImageReader(qr_path)
        except Exception:
            qr_image = None

    # Read CSV and process
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        quadrant_x_positions = [0, quadrant_width]  # Left and right columns
        quadrant_y_positions = [page_height - quadrant_height - vertical_gap - 20, vertical_gap]  # Adjusted top and bottom rows

        quadrant_index = 0  # Track which quadrant we're filling
        for row in reader:
            number, project_name = row

            # Determine the current quadrant's position
            x_start = quadrant_x_positions[quadrant_index % 2]
            y_start = quadrant_y_positions[quadrant_index // 2]

            # Number (large font)
            c.setFont("Helvetica-Bold", number_font_size)
            c.drawCentredString(
                x_start + quadrant_width / 2,
                y_start + quadrant_height / 2 + 20,  # Adjust for vertical centering
                number
            )

            # Project Name (split into two lines if necessary)
            wrapped_name = wrap(project_name, width=30)  # Adjust wrap width as needed
            c.setFont("Helvetica", name_font_size)
            for i, line in enumerate(wrapped_name[:2]):  # Limit to 2 lines
                c.drawCentredString(
                    x_start + quadrant_width / 2,
                    y_start + quadrant_height / 2 - (i + 1) * name_line_spacing,
                    line
                )

            # Draw QR image in the quadrant (bottom-right corner) if available
            if qr_image is not None:
                qr_size = min(quadrant_width, quadrant_height) * 0.35
                margin = 12
                qr_x = x_start + quadrant_width - qr_size - margin
                qr_y = y_start + margin
                try:
                    c.drawImage(qr_image, qr_x, qr_y, width=qr_size, height=qr_size, preserveAspectRatio=True, mask='auto')
                except Exception:
                    # If drawing fails for any reason, ignore and continue
                    pass

            # Move to the next quadrant
            quadrant_index += 1
            if quadrant_index >= 4:  # Reset to the next page after filling all quadrants
                quadrant_index = 0
                draw_footer(c, footer_text)
                c.showPage()

        draw_footer(c, footer_text)
        c.save()


for filename in os.listdir('.'):
    if filename.startswith('f25') and filename.endswith('.csv'):
        pdf_filename = filename[:-4] + '.pdf'
        create_pdf_from_csv(filename, pdf_filename, footer_text=filename[:-4])
