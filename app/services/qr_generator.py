import io
import qrcode
import qrcode.image.svg

def generate_qr_code(url: str, format: str = "png", fill_color: str = "black", back_color: str = "white") -> bytes:
    """
    Generate a QR code and return it as bytes.
    :param url: The URL to encode in the QR code.
    :param format: 'png' or 'svg'
    :param fill_color: Color of the QR modules
    :param back_color: Background color
    """
    # Use SVG image factory if format is SVG
    image_factory = None
    if format == "svg":
        image_factory = qrcode.image.svg.SvgPathImage

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
        image_factory=image_factory,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    img_byte_arr = io.BytesIO()
    if format == "svg":
        img.save(img_byte_arr)
    else:
        # PNG (PIL Image)
        img.save(img_byte_arr, format='PNG')
        
    return img_byte_arr.getvalue()
