# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def get_id(value):
    return re.findall(r"(CVE-\d*-\d*|SVE-\d*-\d*|LVE-\w*-\d*)", value)


def clean_excess_spaces(value):
    return re.sub(r"(^\s*|\s*$)", "", value)


def clean_before_semicolon(value):
    useless_words = "([Ii]mpact|[Ss]everity|[Aa]ffected|CVE|SVE)"
    res = re.sub(r"^.*"+useless_words+r".*:\s*", "", value)
    return res


class BulletCVE(scrapy.Item):
    bullet_title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_excess_spaces)
    )
    cve_id = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_id)
    )
    cust_id = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_id),
    )
    title = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, clean_excess_spaces),
    )
    links = scrapy.Field()
    descr = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    affected = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    severity = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon),
    )
    type = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_excess_spaces),
    )
    patch = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_excess_spaces),
    )

    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()
    server = scrapy.Field()
    date = scrapy.Field()
    pass


class BulletArticle(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_excess_spaces),
    )

    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()
    server = scrapy.Field()
    date = scrapy.Field()
    pass
