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
    filemode='w',  # 'a' means append (add logs to the same file across runs)
    format='%(levelname)s: %(message)s',
    level=logging.CRITICAL
)

# Ensure logging is configured to capture Scrapy logs.
logging.getLogger('scrapy').propagate = True



settings = get_project_settings()
settings.set('TIME_ZONE' , 'Europe/Berlin')

settings.set('ITEM_PIPELINES', {
    'xCrawler.custom_images_pipeline.CustomImagesPipeline':100,
    'xCrawler.pipelines.MysqlConnectorPipeline': 300
    
})
settings.set('EXTENSIONS', { 
    'xCrawler.custom_timezone_extension.TimeZoneExtension': 400,
    'xCrawler.custom_extension.CrawlStatsLogger': 600,  # Adjusted to ensure it logs after notifications  
    'xCrawler.slack_webhook_extension.SpiderCloseSlackNotifier': 200,  # After email, before stats logging
  
})



 





if __name__ == "__main__":
    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider)
    process.start()


