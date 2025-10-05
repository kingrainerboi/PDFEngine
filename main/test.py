from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Create a PDF file
pdf_file = "output.pdf"
c = canvas.Canvas(pdf_file,pagesize= A4)

#defaults
width,height = A4
defualt_text_start = {"x":width -560, "y": height - 50}
defualt_font_size = 20
defualt_font = "Helvetica"



# Draw text on the page
c.setFont(defualt_font,defualt_font_size)
c.drawString(defualt_text_start["x"], defualt_text_start["y"], "hellO")  # (x, y) position, text

# Save the PDF
c.save()

print(f"PDF '{pdf_file}' has been created.")