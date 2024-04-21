import hashlib
import os
from io import BytesIO
from PIL import Image
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.utils.python import to_bytes


class CustomImagesPipeline(ImagesPipeline):

    def __init__(self, store_uri, *args, **kwargs):
        super().__init__(store_uri, *args, **kwargs)



    def get_media_requests(self, item, info):
        if item.get('skip_images'):
            return []  # Skip processing by not generating any media requests
        return super().get_media_requests(item, info)

    
    

    def file_path(self, request, response=None, info=None, *, item=None):
        image_url_hash = hashlib.shake_256(request.url.encode()).hexdigest(5)
        image_perspective = request.url.split("/")[-2]
        image_filename = f"{image_url_hash}_{image_perspective}.jpg"

        return image_filename
    

    def item_completed(self, results, item, info):
        if not all(ok for ok, _ in results):
            raise DropItem(f"Image download failed for {item['uuid']}")
        
        # Count how many images have been downloaded successfully
        successful_downloads = sum(ok for ok, _ in results)
        if successful_downloads == 0:
            raise DropItem(f"Image download failed for {item['uuid']}")

        # Set the item's image_count to the number of successful downloads
        item['image_count'] = successful_downloads

        folder_path = os.path.join(self.store.basedir, item['uuid'])

        
        os.makedirs(folder_path, exist_ok=True)  # Ensure the target directory exists

        self.write_item_info(item, folder_path)  # Write item info to a text file

        image_index = 1
        for ok, result_info in results:
            if ok:
                source_path = os.path.join(self.store.basedir, result_info['path'])
                with open(source_path, 'rb') as f:
                    image_bytes = f.read()
                converted_data = self.convert_image_to_webp(image_bytes, folder_path, image_index)
                image_index += 1
                os.remove(source_path)  # Remove the original downloaded file

        return item

    def write_item_info(self, item, folder_path):
        info_file_path = os.path.join(folder_path, "info.txt")
        with open(info_file_path, 'w') as file:
            for key, value in item.items():
                if key not in ['images', 'image_urls']:
                    file.write(f"{key.capitalize()}: {value}\n")

    def convert_image_to_webp(self, image_bytes, folder_path, image_index):
        # """Converts an image to WebP format and saves it with incrementing filename."""
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')  # Convert to RGB in case it's not
        webp_filename = f"{image_index}.webp"
        webp_path = os.path.join(folder_path, webp_filename)
        image.save(webp_path, 'webp', quality=75)  # Adjust quality as needed
        return webp_path
