# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose
from w3lib.html import remove_tags


def get_id(value):
    ids = re.findall(r"(CVE-\d*[-\d]*|SVE-\d*[-\d]*|LVE-\w*[-\d]*)", value)
    return ids


def format_text(value):
    # delete spaces at begin and end
    value = re.sub(r"(^\s*|\s*$)", "", value)
    # delete NBSP
    value = re.sub(r"\\x[Aa]0", " ", value)
    # reduce spaces
    value = re.sub(r"\s(\s)", "", value)
    return value


def clean_before_semicolon(value):
    useless_words = "([Ii]mpact|[Ss]everity|[Aa]ffected|[Rr]eported|CVE|SVE)"
    res = re.sub(r"^.*"+useless_words+r".*[:：]\s*", "", value)
    return res


class BulletBase(scrapy.Item):
    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()
    server = scrapy.Field()
    date = scrapy.Field()


class BulletCVE(BulletBase):
    bullet_title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text)
    )
    cve_names = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_id)
    )
    title = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, format_text),
    )
    description = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, format_text),
    )
    affected = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, format_text),
    )
    severity = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, format_text),
    )
    reported = scrapy.Field(
        input_processor=MapCompose(
            remove_tags, clean_before_semicolon, format_text),
    )
    weakness = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
    )
    patch = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
    )
    links = scrapy.Field()
    pass


class BulletArticle(BulletBase):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
    )
    pass
