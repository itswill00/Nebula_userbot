from PIL import Image, ImageOps


def resize_image(input_path: str, output_path: str, size=(512, 512)):
    """Mengubah ukuran gambar agar sesuai dengan standar Sticker Telegram (512x512)."""
    with Image.open(input_path) as img:
        img = ImageOps.contain(img, size)
        img.save(output_path, "PNG")
    return output_path


def convert_to_sticker(input_path: str, output_path: str):
    """Konversi gambar ke format PNG transparan untuk sticker."""
    with Image.open(input_path) as img:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.thumbnail((512, 512))
        img.save(output_path, "PNG")
    return output_path
