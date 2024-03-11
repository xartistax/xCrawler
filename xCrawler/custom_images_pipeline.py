from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
import hashlib
import os

class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{item["crawl_date"]}/{item["uuid"]}/{image_guid}.jpg'
    
    def item_completed(self, results, item, info):
        # Call the superclass method to ensure images are handled as usual
        super_result = super().item_completed(results, item, info)
        
        # Define the directory based on item information
        folder_path = os.path.join(self.store.basedir, item['crawl_date'], item['uuid'])
        
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
        
        # Return the result from the superclass method
        return super_result
