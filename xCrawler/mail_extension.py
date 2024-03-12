import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scrapy import signals

class SpiderCloseMailSender:
    @classmethod
    def from_crawler(cls, crawler):
        # Instantiate the extension object
        ext = cls()
        ext.crawler = crawler

        # Connect the extension object to the spider_closed signal
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    def spider_closed(self, spider, reason):
        # Email settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587  # For TLS
        smtp_user = "demianfueglistaler@gmail.com"
        smtp_password = "hwwn vbhn npue lydb"  # Use your app password here
        recipient = "demianfueglistaler@icloud.com"  # Where the email will be sent

        # Prepare the stats to be included in the email
        stats = self.crawler.stats.get_stats()
        stats_message = '\n'.join([f'{k}: {v}' for k, v in stats.items()])

        # Email content
        subject = f"Spider {spider.name} Closed"
        body = f"Spider: {spider.name} has closed. Reason: {reason}\n\nStats:\n{stats_message}"

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = smtp_user
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Enable security
                server.login(smtp_user, smtp_password)  # Login with mail_id and password
                text = message.as_string()
                server.sendmail(smtp_user, recipient, text)
                spider.logger.info("Email sent successfully.")
        except Exception as e:
            spider.logger.error(f"Failed to send email: {e}")
