# xCrawler Project

xCrawler is a web scraping project built with Scrapy, aimed at extracting and processing information from targeted websites. This project specifically focuses on [xdate.ch](https://www.xdate.ch), scraping data and managing images, including handling tasks such as removing watermarks from downloaded images.

## Features

- Scrape data from listings on xdate.ch
- Download images associated with each listing
- Configure to store data in a MySQL database
- Process images to potentially remove watermarks (note: manual processing steps might be required)

## Installation

This project requires Python 3.6+ and Scrapy. It's recommended to use a virtual environment.

### Clone the Repository

```shell
git clone https://github.com/xartistax/xCrawler.git
cd xCrawler
```

## Configuration
```shell
pip install -r requirements.txt
```

## Install Dependencies
Before running the spider, you need to set up environment variables for your database connection. Replace <your_value> with your actual database credentials.

```shell
export MYSQL_DB=<your_db_name>
export MYSQL_USER=<your_db_user>
export MYSQL_PASS=<your_db_password>
export MYSQL_HOST=<your_db_host>
```

## Running the Spider
````shell
scrapy crawl quotes
````