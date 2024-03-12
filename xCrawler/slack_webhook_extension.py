import requests
from scrapy import signals

class SpiderCloseSlackNotifier:
    @classmethod
    def from_crawler(cls, crawler):
        # Instantiate the extension object
        ext = cls()
        ext.crawler = crawler

        # Connect the extension object to the spider_closed signal
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # Slack Webhook URL (Replace with your actual Webhook URL)
        ext.webhook_url = 'https://hooks.slack.com/services/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'

        return ext

    def spider_closed(self, spider, reason):
        # Prepare the stats to be included in the message
        stats = self.crawler.stats.get_stats()
        stats_message = '\n'.join([f'{k}: {v}' for k, v in stats.items()])

        # Slack message content
        message = {
            "text": f"Spider: *{spider.name}* has closed.\nReason: {reason}\n\n*Stats:*\n```{stats_message}```"
        }

        # Send the message to Slack
        response = requests.post(self.webhook_url, json=message)

        # Log success or failure
        if response.status_code == 200:
            spider.logger.info("Slack notification sent successfully.")
        else:
            spider.logger.error(f"Failed to send Slack notification. Status code: {response.status_code}")
