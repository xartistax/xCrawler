import sys
sys.path.append('xCrawler')
from scrapy.pipelines.images import ImagesPipeline
from image_utils import crop_bottom_20px
from image_utils import compress_image
from scrapy.utils.python import to_bytes
import hashlib
import os
import scrapy


class CustomImagesPipeline(ImagesPipeline):
    

    def get_media_requests(self, item, info):
        if item.get('skip_images'):
            return []  # Skip the processing by not generating any media requests
        return super().get_media_requests(item, info)


    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # return f'{item["crawl_date"]}/{item["uuid"]}/{image_guid}.jpg'
        return f'{item["uuid"]}/{image_guid}.jpg'
    
    def item_completed(self, results, item, info):
        if item.get('skip_images'):
            return item
    
        # Call the superclass method to ensure images are handled as usual
        super_result = super().item_completed(results, item, info)
        
        # Define the directory based on item information
        folder_path = os.path.join(self.store.basedir, item['uuid'])
        
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Define the path for the text file
        file_path = os.path.join(folder_path, "info.txt")
        
        # Write the informations to the text file
        with open(file_path, 'w') as file:
            file.write(f"Title: {item.get('title', 'N/A')}\n")
            file.write(f"Text: {item.get('text', 'N/A')}\n")
            file.write(f"Phone: {item.get('phone', 'N/A')}\n")
            file.write(f"Category: {item.get('category', 'N/A')}\n")
            file.write(f"Location: {item.get('location', 'N/A')}\n")
            file.write(f"Address: {item.get('address', 'N/A')}\n")
            file.write(f"Services: {item.get('services', 'N/A')}\n")
            file.write(f"URL: {item.get('url', 'N/A')}\n")
            file.write(f"Origin: {item.get('origin', 'N/A')}\n")

        for ok, result_info in results:
            if ok:
                # The path where the image has been saved
                image_path = os.path.join(self.store.basedir, result_info['path'])
                # Crop the image
                crop_bottom_20px(image_path)
                compress_image(image_path, image_path)

        # New code to rename the first downloaded image
        first_image_info = next((res for res in results if res[0]), None)
        if first_image_info:
            old_path = os.path.join(self.store.basedir, first_image_info[1]['path'])
            new_filename = '1.jpg'  # Or 'first.jpg'
            new_path = os.path.join(folder_path, new_filename)

            # Check if the new path already exists to avoid overwriting
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                # Optionally update the 'path' in results to reflect the new filename
                first_image_info[1]['path'] = os.path.join(item['uuid'], new_filename)
            else:
                print(f"File {new_filename} already exists. Skipping rename.")

        # Return the result from the superclass method
        return super_result
