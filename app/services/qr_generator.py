import io
import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import qrcode
import qrcode.image.svg


def generate_qr_code(
    url: str,
    format: str = "png",
    fill_color: str = "black",
    back_color: str = "white",
    center_text: Optional[str] = None,
    logo_path: Optional[str] = None,
    label_text: Optional[str] = None,
) -> bytes:
    """
    Generate a branded, identifiable QR code and return it as bytes.
    Supports custom brand colors, center initial/logo badge, and bottom identifier banners.
    """
    image_factory = None
    if format == "svg":
        image_factory = qrcode.image.svg.SvgPathImage

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
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

    # 1. Embed Center Badge / Logo
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
            logo.thumbnail((badge_size - 8, badge_size - 8), Image.Resampling.LANCZOS)
            badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
            badge_draw = ImageDraw.Draw(badge)
            badge_draw.rounded_rectangle(
                [0, 0, badge_size, badge_size],
                radius=badge_size // 4,
                fill="white",
                outline=fill_color if fill_color != "white" else "#18181b",
                width=2
            )
            lw, lh = logo.size
            badge.paste(logo, ((badge_size - lw) // 2, (badge_size - lh) // 2), logo)
            img.paste(badge, badge_box, badge)
            badge_drawn = True
        except Exception:
            badge_drawn = False

    if not badge_drawn and center_text:
        badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
        badge_draw = ImageDraw.Draw(badge)
        badge_draw.rounded_rectangle(
            [0, 0, badge_size, badge_size],
            radius=badge_size // 4,
            fill="white",
            outline=fill_color if fill_color != "white" else "#18181b",
            width=2
        )
        initials = center_text[:3].upper()
        badge_draw.text(
            (badge_size // 2, badge_size // 2),
            initials,
            fill=fill_color if fill_color != "white" else "#18181b",
            anchor="mm"
        )
        img.paste(badge, badge_box, badge)

    # 2. Embed Bottom Label Banner if requested (e.g. for standalone downloaded images)
    if label_text:
        banner_height = 44
        final_img = Image.new("RGBA", (w, h + banner_height), (255, 255, 255, 255))
        final_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(final_img)
        draw.line([(16, h), (w - 16, h)], fill="#e4e4e7", width=1)
        draw.text((w // 2, h + (banner_height // 2)), label_text, fill="#18181b", anchor="mm")
        img = final_img

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()
