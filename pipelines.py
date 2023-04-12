# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import socket
import time

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BulletPipeline:
    def process_item(self, item, spider: scrapy.Spider):
        item["url"] = spider.url
        item["project"] = spider.settings.get("BOT_NAME", "unknown")
        item["spider"] = spider.name
        item["server"] = socket.gethostname()
        item["date"] = int(time.time())
        return item
