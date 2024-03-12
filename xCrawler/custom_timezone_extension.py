from scrapy import signals
from datetime import datetime
from zoneinfo import ZoneInfo  # Use pytz for older Python versions

class TimeZoneExtension:
    def __init__(self, tz_name):
        self.tz = ZoneInfo(tz_name)
    
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your extension.
        # You can add settings for your time zone name here, e.g., 'America/New_York'
        tz_name = crawler.settings.get('TIME_ZONE', 'UTC')
        ext = cls(tz_name)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        return ext
    
    def spider_opened(self, spider):
        # Example: Adjusting the spider's start time to the specified time zone
        spider.start_time = datetime.now(self.tz)
