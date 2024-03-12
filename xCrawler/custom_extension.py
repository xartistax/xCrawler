import os
from scrapy import signals
from datetime import datetime

class CrawlStatsLogger:
    def __init__(self, stats):
        self.stats = stats
        self.start_time = None
        self.item_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        # Instantiate the extension object
        ext = cls(crawler.stats)

        # Connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        # Return the extension object
        return ext

    def spider_opened(self, spider):
        self.start_time = datetime.now()

    def spider_closed(self, spider, reason):
        stop_time = datetime.now()
        duration = stop_time - self.start_time
        stats = self.stats.get_stats()
        total_items_scraped = self.stats.get_value('item_scraped_count', 0)
        items_stored_in_db = self.stats.get_value('items_stored_in_db', 0)

        # Specify your desired directory here
        directory = './stats/'
        # Ensure directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Use the directory in your file path
        file_path = os.path.join(directory, f"{spider.name}_crawl_stats_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        
        # Writing stats to the file in the specified directory
        with open(file_path, "w") as file:
            file.write(f"Spider name: {spider.name}\n")
            file.write(f"Start time: {self.start_time}\n")
            file.write(f"Stop time: {stop_time}\n")
            file.write(f"Duration: {duration}\n")
            file.write(f"Total number of items scraped: {total_items_scraped}\n")
            file.write(f"Total number stored in db: {items_stored_in_db}\n\n\n")
            file.write(f"Additional stats:\n")
            for key, value in stats.items():
                file.write(f"{key}: {value}\n")

    def item_scraped(self, item, response, spider):
        self.item_count += 1
