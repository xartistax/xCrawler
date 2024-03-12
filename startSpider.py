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
    'xCrawler.pipelines.MysqlConnectorPipeline': 100,
    'xCrawler.custom_images_pipeline.CustomImagesPipeline': 200
})
settings.set('EXTENSIONS', { 
    'xCrawler.custom_timezone_extension.TimeZoneExtension': 400,
'xCrawler.custom_extension.CrawlStatsLogger': 600,  # Adjusted to ensure it logs after notifications
'xCrawler.mail_extension.SpiderCloseMailSender': 100,   
'xCrawler.slack_webhook_extension.SpiderCloseSlackNotifier': 200,  # After email, before stats logging
  
})

settings.set('TIME_ZONE' , 'Europe/Berlin')
settings.set('MAIL_FROM', 'demianfueglistaler@gmail.com')
settings.set('MAIL_HOST', 'smtp.gmail.com')
settings.set('MAIL_PORT', 465)  # Correct port for TLS
settings.set('MAIL_USER', 'demianfueglistaler@gmail.com')
settings.set('MAIL_PASS', 'hwwn vbhn npue lydb')  # Use an App Password
settings.set('MAIL_TLS', False)
settings.set('MAIL_SSL', True)
 





if __name__ == "__main__":
    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider)
    process.start()


