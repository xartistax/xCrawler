import scrapy
import uuid
import requests
import os
from datetime import datetime
import re
from urllib.parse import urlencode, urlparse, parse_qs




            

 


API_KEY = '237152dd-b110-4915-9b43-c88fcee1361a'


def extract_last_digits(url):
        match = re.search(r'(\d+)$', url)
        if match:
            return match.group(1)  # Returns the matched digits
        else:
            return None  # No digits found





def get_total_pages(pagination_str):
    try:
        total_pages = int(pagination_str.split('/')[1].strip())
        return total_pages
    except (IndexError, ValueError):
        print(f"Error: Invalid pagination string format '{pagination_str}'. Expected format 'current_page / total_pages'.")
        return None

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'bypass': 'cloudflare'}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url
    


class QuotesSpider(scrapy.Spider):
    name = "xdate"
    currentPage = 1
    base_url = "https://www.xdate.ch"
    operating_url = base_url + "/de/filter/p/"
    start_urls = [operating_url + str(currentPage)]
    hrefs = []  # Initialize an empty list to store href values
    debug_mode = True  # Set to False for live mode
    debug_limit = 10 if debug_mode else float('inf')
    folder_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    


    def __init__(self, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.base_path = 'crawls'  # Define base path once, if it's static

    def parse(self, response):
        totalPagesValue = response.xpath('/html/body/div[1]/div[2]/nav/ul/li[2]/input/@value').get()
        total_pages = get_total_pages(totalPagesValue)

        for box in response.xpath('/html/body/div[1]/div[2]/div[6]/div'):
            href = box.css('.ad-teaser::attr(href)').get()
            if href:
                self.hrefs.append(self.base_url + href)  # Append full URL to the list
                
        # Check if the debug limit or total pages limit has been reached; if not, continue to the next page
        if self.currentPage < min(self.debug_limit, total_pages):
            self.currentPage += 1
            next_page_url = self.operating_url + str(self.currentPage)
            #yield scrapy.Request(next_page_url, callback=self.parse)
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            # Debugging: only process up to debug_limit pages
            for hrefLink in self.hrefs:
                #yield scrapy.Request(hrefLink, callback=self.parseContent)
                yield scrapy.Request(hrefLink, callback=self.parseContent)

    def parseContent(self, response):
        # Generate a UUID string for the folder name
        uuid_str = str(uuid.uuid4())  # Fixed variable name and removed the trailing comma

        
        
 
        # Continue with your logic
        ul = response.css('ul.service-list')
        li_texts = ul.css('li::text').getall()

        #all important values
        title = response.css('h1.ad-detail-title::text').get() or 'NaN'
        text_content = ' '.join(response.css('.expandable-text__text.js-is-truncated-text::text').extract())
        if not text_content:
            text_content = 'NaN'
        phone_number = response.css('.phone-number::text').get()
        if phone_number:
            phone = phone_number.replace(" ", "")
        else:
            phone = 'NaN'
        category_texts = response.xpath('/html/body/div[1]/div[2]/div[8]/div[1]/div[1]/div[1]/text()').extract()
        category = category_texts[1].strip() if len(category_texts) > 1 else 'NaN'
        location_extracted = response.xpath('/html/body/div[1]/div[2]/div[8]/div[1]/div[1]/div[2]/text()').extract()
        location = location_extracted[1].strip() if len(location_extracted) > 1 else 'NaN'

        address = ' '.join(response.xpath('//*[@id="contact"]/p[2]/text()').extract()) or 'NaN'
        if not address:
            address = 'NaN'

        services = ', '.join([text.strip() for text in li_texts]) or 'NaN'
        url = response.css('.contact-btn--website::attr(href)').get() or 'NaN'
        origin = response.url
        images = response.css('div.ad-gallery__cell picture img::attr(src)').extract()
        

        item = {
            'uuid': uuid_str,
            'orgin_id' : extract_last_digits(origin),
            'crawl_date': self.folder_name,
            'title': title,
            'text': text_content,
            'phone': phone,
            'category': category,
            'location': location,
            'address': address,
            'services': services,
            'url': url,
            'origin': origin,
            'image_urls': images
        }


        yield item
        return
