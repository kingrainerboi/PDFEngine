from reportlab.lib import colors

# Predefined color name map
COLORS = {
    "black": colors.black,
    "white": colors.white,
    "red": colors.red,
    "green": colors.green,
    "blue": colors.blue,
    "yellow": colors.yellow,
    "cyan": colors.cyan,
    "magenta": colors.magenta,
    "gray": colors.gray,
    "darkgray": colors.darkgray,
    "lightgray": colors.lightgrey,
    "orange": colors.orange,
    "pink": colors.pink,
    "purple": colors.purple,
    "brown": colors.brown,
    "navy": colors.navy,
    "teal": colors.teal,
    "gold": colors.HexColor("#FFD700"),
    "silver": colors.HexColor("#C0C0C0"),
    "lime": colors.HexColor("#00FF00"),
    "indigo": colors.HexColor("#4B0082"),
    "violet": colors.HexColor("#EE82EE"),
    "maroon": colors.HexColor("#800000"),
    "olive": colors.HexColor("#808000"),
    "aqua": colors.HexColor("#00FFFF"),
    "skyblue": colors.HexColor("#87CEEB"),
    "hotpink": colors.HexColor("#FF69B4"),
    "crimson": colors.HexColor("#DC143C"),
    "royalblue": colors.HexColor("#4169E1"),
    "chartreuse": colors.HexColor("#7FFF00"),
    "chocolate": colors.HexColor("#D2691E"),
}


def get_color(value):
    """
    Convert a string into a ReportLab color object.

    Supports:
    - Named colors (e.g., "red", "blue", "gold")
    - Hex colors (e.g., "#FF00FF", "FF00FF")
    - RGB format (e.g., "rgb(255,0,128)")

    Returns a ReportLab color object or black if invalid.
    """
    if not value:
        return colors.black

    value = value.strip().lower()

    # Named color
    if value in COLORS:
        return COLORS[value]

    # Hex color
    if value.startswith("#") or (len(value) == 6 and all(c in "0123456789abcdef" for c in value)):
        try:
            if not value.startswith("#"):
                value = "#" + value
            return colors.HexColor(value)
        except Exception:
            return colors.black

    # RGB format
    if value.startswith("rgb(") and value.endswith(")"):
        try:
            nums = value[4:-1].split(",")
            r, g, b = [int(x.strip()) / 255 for x in nums]
            return colors.Color(r, g, b)
        except Exception:
            return colors.black

    # Fallback
    return colors.black