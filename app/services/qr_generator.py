import io
import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import qrcode
import qrcode.image.svg


def draw_google_g_badge(size: int) -> Image.Image:
    """Creates a high-resolution, crisp Google 'G' review center badge."""
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    # Rounded white background with subtle shadow border
    radius = size // 5
    draw.rounded_rectangle(
        [2, 2, size - 2, size - 2],
        radius=radius,
        fill=(255, 255, 255, 255),
        outline=(228, 228, 231, 255),
        width=2,
    )

    # Google G coordinates scaled to badge size
    center = size / 2.0
    outer_r = size * 0.32
    inner_r = size * 0.18
    thickness = outer_r - inner_r

    # Google Brand Colors
    c_blue = (66, 133, 244, 255)
    c_red = (234, 67, 53, 255)
    c_yellow = (251, 188, 5, 255)
    c_green = (52, 168, 83, 255)

    # Draw circular arcs for Google G
    box = [center - outer_r, center - outer_r, center + outer_r, center + outer_r]
    w_line = int(thickness * 1.05)

    # Yellow arc (bottom-left)
    draw.arc(box, start=140, end=240, fill=c_yellow, width=w_line)
    # Green arc (bottom-right)
    draw.arc(box, start=45, end=145, fill=c_green, width=w_line)
    # Red arc (top)
    draw.arc(box, start=235, end=330, fill=c_red, width=w_line)
    # Blue arc and horizontal bar (top-right & center bar)
    draw.arc(box, start=325, end=405, fill=c_blue, width=w_line)

    # Horizontal center bar
    bar_left = int(center - (size * 0.04))
    bar_right = int(center + outer_r - 2)
    bar_top = int(center - (thickness / 2.0))
    bar_bottom = int(center + (thickness / 2.0))
    draw.rectangle([bar_left, bar_top, bar_right, bar_bottom], fill=c_blue)

    return badge


def generate_qr_code(
    url: str,
    format: str = "png",
    fill_color: str = "#000000",
    back_color: str = "#FFFFFF",
    center_text: Optional[str] = None,
    logo_path: Optional[str] = None,
    label_text: Optional[str] = None,
    badge_style: str = "google",
) -> bytes:
    """
    Generate an ultra-crisp, high-contrast QR code with Google badge and label support.
    """
    image_factory = None
    if format == "svg":
        image_factory = qrcode.image.svg.SvgPathImage

    # High-density box_size for razor-sharp rendering on retina screens and print
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=3,
        image_factory=image_factory,
    )
    qr.add_data(url)
    qr.make(fit=True)

    if format == "svg":
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr)
        return img_byte_arr.getvalue()

    # PNG Format (PIL)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    w, h = img.size

    # 1. Embed Center Badge (Google Review 'G' icon or custom logo)
    badge_size = int(w * 0.22)
    center_x, center_y = w // 2, h // 2
    badge_box = (
        center_x - badge_size // 2,
        center_y - badge_size // 2,
        center_x + badge_size // 2,
        center_y + badge_size // 2,
    )

    badge_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((badge_size - 10, badge_size - 10), Image.Resampling.LANCZOS)
            badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(badge)
            bdraw.rounded_rectangle(
                [0, 0, badge_size, badge_size],
                radius=badge_size // 4,
                fill="white",
                outline=(228, 228, 231, 255),
                width=2
            )
            lw, lh = logo.size
            badge.paste(logo, ((badge_size - lw) // 2, (badge_size - lh) // 2), logo)
            img.paste(badge, badge_box, badge)
            badge_drawn = True
        except Exception:
            badge_drawn = False

    if not badge_drawn:
        # Draw high-res Google G icon badge
        g_badge = draw_google_g_badge(badge_size)
        img.paste(g_badge, badge_box, g_badge)

    # 2. Embed Bottom Label Banner if requested (for downloaded images)
    if label_text:
        banner_height = 54
        final_img = Image.new("RGBA", (w, h + banner_height), (255, 255, 255, 255))
        final_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(final_img)
        draw.line([(20, h), (w - 20, h)], fill=(228, 228, 231, 255), width=2)
        
        # Draw clean uppercase label text
        draw.text((w // 2, h + (banner_height // 2)), label_text.upper(), fill=(24, 24, 27, 255), anchor="mm")
        img = final_img

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG", quality=95)
    return img_byte_arr.getvalue()
