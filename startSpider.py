from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from xCrawler.spiders.spider import QuotesSpider  # Update with your project and spider names
import os

settings=get_project_settings()
settings.set('ITEM_PIPELINES', {
    'xCrawler.custom_images_pipeline.CustomImagesPipeline': 1,
    'xCrawler.pipelines.MysqlConnectorPipeline': 2
})


if __name__ == "__main__":
    process = CrawlerProcess(settings)
    process.crawl(QuotesSpider)
    process.start()
