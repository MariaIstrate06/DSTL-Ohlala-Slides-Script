import io
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PyPDF2 import PdfReader, PdfWriter
import csv
import os
import copy

# Register the font
pdfmetrics.registerFont(TTFont("Montserrat-Bold", "Montserrat-Bold.ttf"))

# Constants
FONT = "Montserrat-Bold"
FONT_SIZE = 50
YELLOW = HexColor("#FFF406")
PINK = HexColor("#D225B4")
LINE_HEIGHT = FONT_SIZE * 1.2
TOP_MARGIN = 200
BOTTOM_MARGIN = 100


def wrap_text(text, max_width, canvas):

    lines = text.splitlines()
    wrapped_lines = []

    for line in lines:
        words = line.split(" ")
        current_line = ""
        for word in words:

            test_line = f"{current_line} {word}".strip()
            if canvas.stringWidth(test_line, FONT, FONT_SIZE) < max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word

        wrapped_lines.append(current_line)  # Add the last part of the line

    return wrapped_lines


def add_text_to_page(template_page, text, color, page_width, page_height):

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFont(FONT, FONT_SIZE)
    c.setFillColor(color)

    lines = wrap_text(text, page_width - 40, c)
    total_lines = len(lines)

    available_height = page_height - TOP_MARGIN - BOTTOM_MARGIN

    total_text_height = total_lines * LINE_HEIGHT
    if total_text_height < available_height:
        y = (available_height - total_text_height) / 2 + TOP_MARGIN
    else:

        y = TOP_MARGIN


    for line in lines:
        text_width = c.stringWidth(line, FONT, FONT_SIZE)
        x = (float(page_width) - text_width) / 2
        c.drawString(x, y, line)
        y -= LINE_HEIGHT

    c.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    template_page.merge_page(new_pdf.pages[0])


def generate_presentation(input_csv, template_pdf, output_pdf):

    template_reader = PdfReader(template_pdf)
    template_pages = [template_reader.pages[i] for i in range(len(template_reader.pages))]
    writer = PdfWriter()

    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            first_lyrics = row['text1']
            last_lyrics = row['text2']

            page_width = float(template_pages[0].mediabox[2])
            page_height = float(template_pages[0].mediabox[3])


            page1 = copy.deepcopy(template_pages[0])
            add_text_to_page(page1, first_lyrics, YELLOW, page_width, page_height)
            writer.add_page(page1)


            writer.add_page(template_pages[1])

            page3 = copy.deepcopy(template_pages[2])
            add_text_to_page(page3, last_lyrics, PINK, page_width, page_height)
            writer.add_page(page3)

    with open(output_pdf, "wb") as final_pdf:
        writer.write(final_pdf)
    print(f"Final PDF created: {output_pdf}")


generate_presentation("test2.csv", "template.pdf", "output_presentation.pdf")
