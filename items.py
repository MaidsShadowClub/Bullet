# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def clean_before_semicolon(value):
    res = re.sub(r".*:\s*", "", value)
    return res


class BulletCVE(scrapy.Item):
    cve_id = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, lambda i: re.search(r"CVE-\d*-\d*", i)),
        output_processor=TakeFirst()
    )
    cust_id = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, lambda i: re.search(r"SVE-\d*-\d*", i)),
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    links = scrapy.Field()
    descr = scrapy.Field()
    affected = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    severity = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    type = scrapy.Field()
    patch = scrapy.Field()

    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()
    server = scrapy.Field()
    date = scrapy.Field()
    pass
