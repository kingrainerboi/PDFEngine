import os.path
import textwrap
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER, A3
from reportlab.lib.pagesizes import portrait, landscape
from res.colors.font_colors import get_color
PAGE_SIZES = {
    "a4": A4,
    "letter": LETTER,
    "a3": A3
}

PAGE_LAYOUTS = {
    "portrait": portrait,
    "landscape": landscape
}


def wrapper(c, text, x, y, font, font_size, color, page_width, align="left", line_spacing=5):
    c.setFont(font, font_size)
    c.setFillColor(get_color(color))
    char_width = font_size * 0.55  # adaptive scaling
    usable_width = page_width - (x * 2)
    max_chars_per_line = max(10, int(usable_width / char_width))

    for line in text.splitlines():
        line = line.lstrip()
        wrapped_lines = textwrap.wrap(line, width=max_chars_per_line)

        for wline in wrapped_lines:
            text_width = c.stringWidth(wline, font, font_size)

            # Alignment math
            match align:
                case "center":
                    text_x = (page_width - text_width) / 2
                case "right":
                    text_x = page_width - text_width - x
                case _:
                    text_x = x  # left

            c.drawString(text_x, y, wline)
            y -= font_size + line_spacing
    return y

class PDFEngine:
    def __init__(self, txt_file):
        self.txt_file = txt_file
        self.pdf_file = "output.pdf"
        self.default_font = "Courier"
        self.default_font_color = get_color("black")
        self.default_font_size = 20
        self.default_x = 50
        self.default_y = 800
        self.default_background_image =""
        self.default_page_layout = portrait
        self.default_page_size = A4
        self.default_text_align = "left"

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
        size_match = re.search(r'font-size\s+"?([^"\n]+)"?', block)
        background_image = re.search(r'background-image\s+"?([^"\n]+)"?', block)
        page_layout = re.search(r'page-layout\s+"?([^"\n]+)"?', block)
        page_size = re.search(r'page-size\s+"?([^"\n]+)"?', block)

        if font_match:
            self.default_font = font_match.group(1)
        if size_match:
            self.default_font_size = int(size_match.group(1))
        if background_image and os.path.exists(background_image.group(1)):
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
        font_color_override = self.default_font_color
        font_align_override = self.default_text_align

        if style_block:
            # Extract all 4-level style instructions
            style_quads = re.findall(r'(\w+)(?:\s+(\w+))?\s+"([^"]+)"', style_block, re.MULTILINE)
            for incom, typecom, val in style_quads:
                incom = incom.strip().lower()
                typecom = (typecom.strip().lower() if typecom else None)
                val = val.strip()


                match command:
                    case "text":
                        match incom:
                            case "text":
                                match typecom:
                                    case "size":
                                        try:
                                            font_size_override = int(val)
                                        except ValueError:
                                            print(f"Invalid font size '{val}'")
                                    case "color":
                                        try:
                                            font_color_override = get_color(val)
                                        except ValueError:
                                            print(f"Invalid color '{val}'")
                                    case "align":
                                        try:
                                            font_align_override = val
                                        except ValueError:
                                            print("not alignment type")
                                    case "style" | None:
                                        font_override = val


                    case "title":
                        match incom:
                            case "title":
                                match typecom:
                                    case "size":
                                        try:
                                            font_size_override = int(val)
                                        except ValueError:
                                            print(f"Invalid title size '{val}'")

                    case _:
                        print(f"Unknown style: {incom} {typecom or ''}")
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
                    font_color_override,
                    width,
                    font_align_override
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
                    font_color_override,
                    width,
                    font_align_override
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
                    font_color_override,
                    width,
                    font_align_override
                )
            case "background-image":
                if os.path.exists(content):
                    width, height = c._pagesize
                    c.drawImage(content, 0, 0, width=width, height=height)
                else:
                    print("no")


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

        # --- Create PDF Canvas ---
        c = canvas.Canvas(self.pdf_file, pagesize=self.default_page_layout(self.default_page_size))
        width, height = c._pagesize

        # --- Dynamically adjust default coordinates depending on layout ---
        if self.default_page_layout == landscape:
            self.default_y = height - 80  # start near top
            self.default_x = 70  # small left margin
        else:
            self.default_y = height - 100  # standard portrait margin
            self.default_x = 50

        # --- Render each page block ---
        for block_type, block_content in page_blocks:
            # Draw background if defined
            if self.default_background_image:
                if os.path.exists(self.default_background_image):
                    c.drawImage(self.default_background_image, 0, 0, width=width, height=height)
                else:
                    print(f"Warning: background image '{self.default_background_image}' not found.")

            # Create page content
            c, _ = self.create(block_type, block_content, c)

        # --- Finalize PDF ---
        c.save()
        print(f"PDF saved as {self.pdf_file}")


# --- Usage ---
engine = PDFEngine("pdflang.pdfs")
engine.interpret()