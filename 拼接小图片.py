from PIL import Image, ImageOps
import os


def vertical_concat(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    new_image = Image.new('RGB', (3000, 5000), (0, 0, 0))
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)
        width, height = image.size
        if width > height:
            new_width = 1000
            new_height = int(height * (1000 / width))
        else:
            new_height = 1000
            new_width = int(width * (1000 / height))
        image = image.resize((new_width, new_height), resample=Image.BICUBIC)
        new_x = (1000 - new_width) // 2 + 1000 * (i // 5)
        new_y = (1000 - new_height) // 2 + 1000 * (i % 5)
        new_image.paste(image, (new_x, new_y))
        #for x in range(new_image.width):
        #    for y in range(new_image.height):
        #        r, g, b = new_image.getpixel((x, y))
        #        if r == 0 and g == 0 and b == 0:
        #            new_image.putpixel((x, y), (17, 17, 17))
    return new_image

folder_path = 'C://Users//seewo//Desktop//new'
result_image = vertical_concat(folder_path)
result_image.save('C://Users//seewo//Desktop//new//result.jpg')
