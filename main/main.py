import textwrap
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER, A3
from reportlab.lib.pagesizes import portrait, landscape

PAGE_SIZES = {
    "a4": A4,
    "letter": LETTER,
    "a3": A3
}

PAGE_LAYOUTS = {
    "portrait": portrait,
    "landscape": landscape
}


def wrapper(c: canvas.Canvas, text, x, y, font, font_size, page_width, line_spacing=5):
    c.setFont(font, font_size)
    max_chars_per_line = int((page_width - x * 2) / (font_size * 0.6))  # approx char width
    for line in text.splitlines():
        line = line.lstrip()
        wrapped_lines = textwrap.wrap(line, width=max_chars_per_line)
        for wline in wrapped_lines:
            c.drawString(x, y, wline)
            y -= font_size + line_spacing
    return y


class PDFEngine:
    def __init__(self, txt_file):
        self.txt_file = txt_file
        self.pdf_file = "output.pdf"
        self.default_font = "Courier"
        self.default_font_size = 20
        self.default_x = 50
        self.default_y = 800
        self.default_background_image =""
        self.default_page_layout = portrait
        self.default_page_size = A4

        self.default_title_size = 25
        self.default_title_font = "Helvetica"


    def read(self):
        with open(self.txt_file, "r") as file:
            return file.read()

    def parse_page_style(self, block):
        """
        Parse default-style block for font, fontsize, background, page layout and size
        """
        font_match = re.search(r'font\s+"?([^"\n]+)"?', block)
        size_match = re.search(r'fontsize\s+"?([^"\n]+)"?', block)
        background_image = re.search(r'background-image\s+"?([^"\n]+)"?', block)
        page_layout = re.search(r'page-layout\s+"?([^"\n]+)"?', block)
        page_size = re.search(r'page-size\s+"?([^"\n]+)"?', block)

        if font_match:
            self.default_font = font_match.group(1)
        if size_match:
            self.default_font_size = int(size_match.group(1))
        if background_image:
            self.default_background_image = background_image.group(1)
        if page_layout:
            layout_str = page_layout.group(1).lower()
            self.default_page_layout = PAGE_LAYOUTS.get(layout_str, portrait)  # fallback to portrait
        if page_size:
            size_str = page_size.group(1).lower()
            self.default_page_size = PAGE_SIZES.get(size_str, A4)  # fallback to A4

    def add(self, command, content, c, current_y, style_block=None):
        # --- Inline style overrides ---
        font_override = self.default_font
        font_size_override = self.default_font_size

        if style_block:
            # Finds all style entries like: font size "40", font name "Courier", etc.
            style_pairs = re.findall(r'([\w-]+)\s+"([^"]+)"', style_block, re.MULTILINE)
            for key, value in style_pairs:
                match key.lower():
                    case "font":
                        font_override = value
                    case "size" | "fontsize" | "font-size":
                        try:
                            font_size_override = int(value.strip())
                        except ValueError:
                            print(f"Warning: invalid font size '{value}'")

        # --- Apply commands ---
        match command:
            case "text":
                width, _ = c._pagesize
                current_y = wrapper(
                    c,
                    textwrap.dedent(content),
                    self.default_x,
                    current_y,
                    font_override,
                    font_size_override,
                    width
                )
            case "title":
                width, _ = c._pagesize
                current_y = wrapper(
                    c,
                    textwrap.dedent(content),
                    self.default_x,
                    current_y,
                    self.default_title_font,
                    self.default_title_size,
                    width
                )
            case "space":
                width, _ = c._pagesize
                current_y = wrapper(
                    c,
                    "",
                    self.default_x,
                    current_y - float(content),
                    self.default_font,
                    self.default_font_size,
                    width
                )
            case "background-image":
                width, height = c._pagesize
                c.drawImage(content, 0, 0, width=width, height=height)
            case _:
                print(f"Unknown add command: {command}")

        return current_y
    def create(self, block_type, block_content, c):
        current_y = self.default_y

        match block_type:
            case "page":
                add_commands = re.findall(
                    r'add\s+([\w-]+)(?:\(([\s\S]*?)\))?\s*"([\s\S\d]*?)"',
                    block_content,
                    re.MULTILINE
                )
                for command, style_block, content in add_commands:
                    current_y = self.add(command, content, c, current_y, style_block)

                c.showPage()

        return c, current_y


    def interpret(self):
        text = self.read()

        # --- Parse title ---
        title_match = re.search(r'title\s+"(.+)"', text)
        if title_match:
            self.pdf_file = title_match.group(1)

        # --- Parse default-style ---
        style_match = re.search(r'page-style\s*\{([\s\S]*?)}', text)
        if style_match:
            self.parse_page_style(style_match.group(1))

        # --- Parse create blocks ---
        page_blocks = re.findall(r'create\s+(\w+)\s+\d*\s*\{([\s\S]*?)}', text)
        if not page_blocks:
            print("No create blocks found.")
            return

        c = canvas.Canvas(self.pdf_file, pagesize=self.default_page_layout(self.default_page_size))
        width,height = c._pagesize
        for block_type, block_content in page_blocks:
            if self.default_background_image:
              c.drawImage(self.default_background_image, 0, 0, width=width, height=height)

            c, _ = self.create(block_type, block_content, c)


        c.save()
        print(f"PDF saved as {self.pdf_file}")


# --- Usage ---
engine = PDFEngine("pdflang.txt")
engine.interpret()