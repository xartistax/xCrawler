from PIL import Image

def crop_bottom_20px(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        crop_box = (0, 0, width, height - 25)
        cropped_img = img.crop(crop_box)
        cropped_img.save(image_path)


from PIL import Image


def compress_image(input_image_path, output_image_path, quality=60):

    img = Image.open(input_image_path)
    img.save(output_image_path, quality=quality, optimize=True)