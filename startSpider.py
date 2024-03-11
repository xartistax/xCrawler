import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from xCrawler.spiders.spider import QuotesSpider  # Update with your project and spider names

# Set up logging
# Ensure the logs directory exists
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

log_file_path = os.path.join(logs_dir, "crawl.log")  # Define your log file name
logging.basicConfig(
    filename=log_file_path,
    filemode='a',  # 'a' means append (add logs to the same file across runs)
    format='%(levelname)s: %(message)s',
    level=logging.WARNING
)

# Ensure logging is configured to capture Scrapy logs.
logging.getLogger('scrapy').propagate = True

settings = get_project_settings()
settings.set('ITEM_PIPELINES', {
    'xCrawler.custom_images_pipeline.CustomImagesPipeline': 1,
    'xCrawler.pipelines.MysqlConnectorPipeline': 2
})

if __name__ == "__main__":
    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider)
    process.start()
