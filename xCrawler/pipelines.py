# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface




import shutil
from itemadapter import ItemAdapter

import mysql.connector
from scrapy.exceptions import DropItem
from scrapy import signals
import random
import os

from openai import OpenAI




class MysqlConnectorPipeline:

    
    
    def __init__(self, stats):
        self.stats = stats
        # Initialize other necessary attributes here

    def delete_folder_if_exists(self, folder_path):
        try:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted folder: {folder_path}")
        except Exception as e:
            print(f"Error deleting folder {folder_path}: {e}")



    def detectAndSetNameWithOpenAI(self , title, description):

        client = OpenAI(
    # This is the default and can be omitted
            api_key=os.environ.get("OPENAI"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please define a Profile Name for the following profile description. Sometimes the name is in the title or in the description itself, then just use this one: {title} - {description}",
                }
            ],
            model="gpt-3.5-turbo",
        )

        return chat_completion.choices[0].message.content



    @classmethod
    def from_crawler(cls, crawler):
        # Instantiate the pipeline with access to the stats collector
        pipeline = cls(crawler.stats)
        return pipeline
    
    def open_spider(self, spider):
        self.stats.set_value('items_stored_in_db', 0)
        db_settings = spider.settings.get('MYSQL_DATABASE')
        self.dbName = db_settings['db']  # Database name from settings
        self.tableName = db_settings['table']  # Table name from settings

        # Connect to MySQL server without specifying a database
        self.conn = mysql.connector.connect(
            host=db_settings['host'],
            user=db_settings['user'],
            password=db_settings['passwd']
        )
        self.cursor = self.conn.cursor()

        # Check if the database exists and create it if it doesn't
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.dbName}`")
        self.conn.commit()

        # Now connect to the newly created or existing database
        self.conn.database = self.dbName

        if spider.debug_mode:
            # If in debug mode spider shoud delete the images folder and delete the table
            self.delete_folder_if_exists('../public/images')

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS `{self.tableName}`")
                self.conn.commit()
                cursor.close()
                print(f"Dropped table: {self.tableName}")

            except mysql.connector.Error as e:
                print(f"Error dropping table {self.tableName}: {e}")

            

        

        

        # Create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{self.tableName}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            uuid VARCHAR(255) NOT NULL,
            orgin_id VARCHAR(255) NOT NULL, 
            crawl_date VARCHAR(255) NOT NULL, 
            title VARCHAR(255) NOT NULL,
            description LONGTEXT NOT NULL,
            name TEXT NOT NULL,
            phone VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            address MEDIUMTEXT NOT NULL,
            services LONGTEXT NOT NULL,
            url VARCHAR(255) NOT NULL,
            origin VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INT DEFAULT 0,
            image_count INT DEFAULT 0
            
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        # Check if an item with the same origin_id already exists
        check_query = f"SELECT EXISTS(SELECT 1 FROM `{self.tableName}` WHERE orgin_id = %s)"
        orgin_id = item.get('orgin_id', 'NO_ORIGIN_ID')

        self.cursor.execute(check_query, (orgin_id,))
        exists = self.cursor.fetchone()[0]

        if exists:
            spider.logger.info(f"Item with origin_id {orgin_id} already exists. Skipping...")
            item['skip_images'] = True
            return item  # Skip this item
        
        if not item.get('images_downloaded', True):
            spider.logger.info(f"Skipping database insertion for {item['uuid']} because images were not downloaded")
            return item

        # If the item does not exist, proceed with insertion
        insert_query = f"INSERT INTO `{self.tableName}` (uuid, orgin_id, crawl_date, title, description, name, phone, category, location, address, services, url, origin, likes, image_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"



        # Fetching item values with more appropriate default values
        uuid = item.get('uuid', 'NO_UUID')
        crawl_date = item.get('crawl_date', 'NO_CRAWL_DATE')
        title = item.get('title', 'NO_TITLE')
        description = item.get('text', 'NO_DESCRIPTION')  # Ensure 'text' is the correct field key
        name = self.detectAndSetNameWithOpenAI(title, description)
        phone = item.get('phone', 'NO_PHONE')
        category = item.get('category', 'NO_CATEGORY')
        location = item.get('location', 'NO_LOCATION')
        address = item.get('address', 'NO_ADDRESS')
        services = item.get('services', 'NO_SERVICES')  # Corrected to 'services' based on table schema
        url = item.get('url', 'NO_URL')
        origin = item.get('origin', 'NO_ORIGIN')
        likes =  int(random.triangular(0, 88, 0)) 
        image_count = item.get('image_count', 0)

        try:
            self.cursor.execute(insert_query, (
            uuid, orgin_id, crawl_date, title,  description, name, phone, category, location, address, services, url, origin, likes, image_count))
            self.conn.commit()

            self.stats.inc_value('items_stored_in_db')
        except mysql.connector.Error as e:
            self.conn.rollback()
            spider.logger.error(f"Error inserting item into database: {e}")
            raise DropItem(f"Error inserting item into database: {item}")



        spider.logger.info(f"Item with origin_id {orgin_id} inserted successfully.")
        print(self.detectAndSetNameWithOpenAI(title, description))
        return item
