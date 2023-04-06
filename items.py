# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BulletItem(scrapy.Item):
    cve_id = scrapy.Field()
    cust_id = scrapy.Field()
    title = scrapy.Field()
    links = scrapy.Field()
    descr = scrapy.Field()
    affected = scrapy.Field()
    severity = scrapy.Field()
    type = scrapy.Field()
    patch = scrapy.Field()
    pass
