import sys
sys.path.append('xCrawler')
from scrapy.pipelines.images import ImagesPipeline
#from image_utils import crop_bottom_20px
from image_utils import compress_image
from scrapy.utils.python import to_bytes
import hashlib
import os
import scrapy
from scrapy.exceptions import DropItem


class CustomImagesPipeline(ImagesPipeline):
    
    def verify_and_correct_image_renames(self, folder_path, expected_count):
        """
        Verifies that images in the given folder are correctly renamed in a sequential order starting from 1.jpg.
        If any discrepancies are found, attempts to correct them.

        Args:
            folder_path (str): The path to the folder containing the images.
            expected_count (int): The expected number of images in the folder.

        Returns:
            int: The actual number of image files in the folder after verification and correction.
        """
        actual_files = sorted(os.listdir(folder_path))  # Get sorted list of files in the directory
        missing_files = []
        image_files = [file for file in actual_files if file.endswith('.jpg') and file[:-4].isdigit()]

        for index in range(1, expected_count + 1):
            expected_filename = f"{index}.jpg"
            if expected_filename not in image_files:
                missing_files.append(expected_filename)

        if missing_files:
            unmatched_files = [file for file in actual_files if not file.endswith('.jpg') or not file[:-4].isdigit()]
            for expected_filename, unmatched_file in zip(missing_files, unmatched_files):
                old_path = os.path.join(folder_path, unmatched_file)
                new_path = os.path.join(folder_path, expected_filename)
                try:
                    os.rename(old_path, new_path)
                    image_files.append(expected_filename)  # Update the list of image files
                except Exception as e:
                    print(f"Error renaming {unmatched_file} to {expected_filename}: {e}")

        # Return the actual count of image files after potential renaming
        return len(image_files)
 
            
        


    def get_media_requests(self, item, info):
        if item.get('skip_images'):
            return []  # Skip the processing by not generating any media requests
        return super().get_media_requests(item, info)


    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # return f'{item["crawl_date"]}/{item["uuid"]}/{image_guid}.jpg'
        return f'{item["uuid"]}/{image_guid}.jpg'
    
    



    def item_completed(self, results, item, info):
        all_images_downloaded = all(ok for ok, _ in results)
        item['images_downloaded'] = all_images_downloaded

        if not all_images_downloaded:
            raise DropItem(f"Drop item because image download failed for {item['uuid']}")

        if item.get('skip_images'):
            return item

        super_result = super().item_completed(results, item, info)
        folder_path = os.path.join(self.store.basedir, item['uuid'])
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "info.txt")
        with open(file_path, 'w') as file:
            # Write information to the file...
            file.write(f"Title: {item.get('title', 'N/A')}\n")
            file.write(f"Text: {item.get('text', 'N/A')}\n")
            file.write(f"Phone: {item.get('phone', 'N/A')}\n")
            file.write(f"Category: {item.get('category', 'N/A')}\n")
            file.write(f"Location: {item.get('location', 'N/A')}\n")
            file.write(f"Address: {item.get('address', 'N/A')}\n")
            file.write(f"Services: {item.get('services', 'N/A')}\n")
            file.write(f"URL: {item.get('url', 'N/A')}\n")
            file.write(f"Origin: {item.get('origin', 'N/A')}\n")

        image_index = 1
        for ok, result_info in results:
            if ok:
                image_path = os.path.join(self.store.basedir, result_info['path'])
                new_filename = f"{image_index}.jpg"
                new_path = os.path.join(folder_path, new_filename)
                try:
                    os.rename(image_path, new_path)
                    image_index += 1
                except OSError as e:
                    # Log the error or handle it as per your requirement
                    print(f"Error renaming image {image_path} to {new_path}: {e}")

        # Optionally, add post-renaming verification here...
        image_count = self.verify_and_correct_image_renames(folder_path, image_index - 1)
        item['image_count'] = image_count
        print(f"image count is:  {image_count}")




        if image_count == 0:
            raise DropItem(f"No images downloaded for {item['uuid']}. Dropping item.")

        
        return super_result
