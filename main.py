import os
import io

import tkinter as tk
from tkinter import filedialog

from PyPDF2 import PdfReader, PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from PIL import Image


# Process to avoid PIL error
def create_watermark(watermark_image_path, margin_x, margin_y, scale=1.0):
    width, height = A4
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    img = Image.open(watermark_image_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Compatable to different watermark size
    w, h = img.size
    scaled_w = int(w * scale)
    scaled_h = int(h * scale)

    temp_img_path = 'temp_watermark.png'
    img.save(temp_img_path, 'PNG')

    can.drawImage(temp_img_path,
                  width - margin_x * mm - scaled_w,
                  height - margin_y * mm - scaled_h,
                  width=scaled_w,
                  height=scaled_h)
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    watermark_page = new_pdf.pages[0]

    os.remove(temp_img_path)

    return watermark_page


def add_watermark_to_pdf(input_pdf_path, watermark_image_path, margin_x_mm,
                         margin_y_mm, output_pdf_path, factor):
    watermark_page = create_watermark(watermark_image_path, margin_x_mm,
                                      margin_y_mm, factor)
    input_pdf = PdfReader(input_pdf_path)
    output_pdf = PdfWriter()

    for page in input_pdf.pages:
        page.merge_page(watermark_page)
        output_pdf.add_page(page)

    with open(output_pdf_path, 'wb') as output_file:
        output_pdf.write(output_file)


def select_input_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        input_pdf_entry.delete(0, tk.END)
        input_pdf_entry.insert(0, file_path)
        # Default output file same as input
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        default_output_name = f"{base_name}_watermark.pdf"
        output_pdf_entry.delete(0, tk.END)
        output_pdf_entry.insert(0, default_output_name)


def select_watermark_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.*")])
    if file_path:
        watermark_image_entry.delete(0, tk.END)
        watermark_image_entry.insert(0, file_path)


def start_processing():
    input_pdf = input_pdf_entry.get()
    watermark_image = watermark_image_entry.get()
    try:
        margin_x = float(margin_x_entry.get())
        margin_y = float(margin_y_entry.get())
        # Get factor
        factor = float(factor_entry.get())
    except ValueError:
        status_label.config(text="Invalid margin or scale value!")
        return
    output_pdf = output_pdf_entry.get()
    if input_pdf and watermark_image and output_pdf:
        try:
            add_watermark_to_pdf(input_pdf, watermark_image, margin_x,
                                 margin_y, output_pdf, factor)
            status_label.config(text="Done!")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
    else:
        status_label.config(text="Make sure all fields are filled!")


# GUI ----------------------------------------------
root = tk.Tk()
root.title("PDF Watermarking Tool")

input_pdf_label = tk.Label(root, text="Input PDF file:")
input_pdf_label.pack(pady=5)
input_pdf_entry = tk.Entry(root, width=50)
input_pdf_entry.pack(pady=5)
input_pdf_button = tk.Button(root,
                             text="Select File",
                             command=select_input_pdf)
input_pdf_button.pack(pady=5)

watermark_image_label = tk.Label(root, text="Watermark file:")
watermark_image_label.pack(pady=5)
watermark_image_entry = tk.Entry(root, width=50)
watermark_image_entry.pack(pady=5)
watermark_image_button = tk.Button(root,
                                   text="Select File",
                                   command=select_watermark_image)
watermark_image_button.pack(pady=5)

margin_x_label = tk.Label(root, text="Margin X (mm) from top-right:")
margin_x_label.pack(pady=5)
margin_x_entry = tk.Entry(root, width=20)
margin_x_entry.insert(0, "10")  # Default 10mm
margin_x_entry.pack(pady=5)

margin_y_label = tk.Label(root, text="Margin Y (mm) from top-right")
margin_y_label.pack(pady=5)
margin_y_entry = tk.Entry(root, width=20)
margin_y_entry.insert(0, "10")  # Default 10mm
margin_y_entry.pack(pady=5)

# Add factor entry for better result
factor_label = tk.Label(root, text="Scale:")
factor_label.pack(pady=5)
factor_entry = tk.Entry(root, width=20)
factor_entry.insert(0, "1.0")
factor_entry.pack(pady=5)

output_pdf_label = tk.Label(root, text="Output PDF file name:")
output_pdf_label.pack(pady=5)
output_pdf_entry = tk.Entry(root, width=50)
output_pdf_entry.pack(pady=5)

process_button = tk.Button(root,
                           text="Start Processing",
                           command=start_processing)
process_button.pack(pady=20)

status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# End of GUI ----------------------------------------------

root.mainloop()
