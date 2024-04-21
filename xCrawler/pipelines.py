import psycopg2
from scrapy.exceptions import DropItem

class PostgresPipeline:
    def open_spider(self, spider):
        # Connect to the PostgreSQL database
        db_settings = spider.settings.get('POSTGRES_DATABASE')
        self.conn = psycopg2.connect(
                database="verceldb",
                host="ep-rough-resonance-a2d0s4rz-pooler.eu-central-1.aws.neon.tech",
                user="default",
                password="WDdbE4LtVZ3e",
                port="5432"
            )

        self.cursor = self.conn.cursor()

    def close_spider(self, spider): 
        # Close the database conn
        self.conn.close()

    def process_item(self, item, spider):
        try:
            # Create the table if it doesn't exist
            self.cursor.execute( """
                CREATE TABLE IF NOT EXISTS xTable (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(255) NOT NULL,
                    orgin_id VARCHAR(255) NOT NULL, 
                    crawl_date VARCHAR(255) NOT NULL, 
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    descriptionFormated TEXT NOT NULL,
                    name TEXT NOT NULL,
                    phone VARCHAR(255) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    location VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    services TEXT NOT NULL,
                    url VARCHAR(255) NOT NULL,
                    origin VARCHAR(255) NOT NULL,
                    created_at VARCHAR(255) NOT NULL
                            
                ); """)

            self.cursor.execute(
                """
                INSERT INTO xTable (uuid, orgin_id, crawl_date, title, description, descriptionFormated, name, phone, category, location, address, services, url, origin,  created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s)
                """,
                (
                    item.get('uuid', 'NO_UUID'),
                    item.get('orgin_id', ''),
                    item.get('crawl_date', ''),
                    item.get('title', ''),
                    item.get('description', ''),
                    item.get('descriptionFormated', ''),
                    item.get('name', ''),
                    item.get('phone', ''),
                    item.get('category', ''),
                    item.get('location', ''),
                    item.get('address', ''),
                    item.get('services', ''),
                    item.get('url', ''),
                    item.get('origin', ''),
                    item.get('created_at', '')
                    
                )
            )

            self.conn.commit()


        except Exception as e:
            # Log any errors and drop the item
            spider.logger.error(f"Error storing item in database: {e}")
            raise DropItem(f"Error storing item in database: {e}")

        return item
