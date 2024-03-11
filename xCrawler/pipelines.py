# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface



from itemadapter import ItemAdapter

import mysql.connector
from scrapy.exceptions import DropItem

class MysqlConnectorPipeline:

    def open_spider(self, spider):
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

        # Create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{self.tableName}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            uuid VARCHAR(255) NOT NULL,
            orgin_id VARCHAR(255) NOT NULL, 
            crawl_date VARCHAR(255) NOT NULL, 
            title VARCHAR(255) NOT NULL,
            description LONGTEXT NOT NULL,
            phone VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            address MEDIUMTEXT NOT NULL,
            services LONGTEXT NOT NULL,
            url VARCHAR(255) NOT NULL,
            origin VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            
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
            item['skip_images'] = True  # Mark the item to skip image processing
            return item  # Skip this item

        # If the item does not exist, proceed with insertion
        insert_query = f"INSERT INTO `{self.tableName}` (uuid, orgin_id, crawl_date, title, description, phone, category, location, address, services, url, origin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Fetching item values with more appropriate default values
        uuid = item.get('uuid', 'NO_UUID')
        crawl_date = item.get('crawl_date', 'NO_CRAWL_DATE')
        title = item.get('title', 'NO_TITLE')
        description = item.get('text', 'NO_DESCRIPTION')  # Ensure 'text' is the correct field key
        phone = item.get('phone', 'NO_PHONE')
        category = item.get('category', 'NO_CATEGORY')
        location = item.get('location', 'NO_LOCATION')
        address = item.get('address', 'NO_ADDRESS')
        services = item.get('services', 'NO_SERVICES')  # Corrected to 'services' based on table schema
        url = item.get('url', 'NO_URL')
        origin = item.get('origin', 'NO_ORIGIN')

        try:
            self.cursor.execute(insert_query, (
            uuid, orgin_id, crawl_date, title, description, phone, category, location, address, services, url, origin))
            self.conn.commit()
        except mysql.connector.Error as e:
            self.conn.rollback()
            spider.logger.error(f"Error inserting item into database: {e}")
            raise DropItem(f"Error inserting item into database: {item}")



        spider.logger.info(f"Item with origin_id {orgin_id} inserted successfully.")
        return item
