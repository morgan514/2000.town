from django import template
from PIL import Image

register = template.Library()

@register.filter
def rotate_image(image_url):
    try:
        img = Image.open(image_url)
        img = img.rotate(img._getexif().get(274, 0), expand=True)
        rotated_image_url = "path_to_rotated_image.jpg"
        img.save(rotated_image_url)
        return rotated_image_url
    except Exception as e:
        return image_url
