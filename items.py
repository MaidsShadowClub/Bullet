# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose
from w3lib.html import remove_tags
from datetime import datetime


def get_cve_names(value):
    regex = (
        r"(" +
        r"CVE-\d{4}-\d*|" +
        r"SVE-\d{4}-\d*-?\d*|" +
        r"LVE-\w*-\d{4,6}" +
        r")"
    )
    ids = re.findall(regex, value)
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
    excess_words_regex = (
        r".*" +  # everything before userless words
        r"(" +
        r"[Ii]mpact|" +
        r"[Ss]everity|" +
        r"[Aa]ffected|" +
        r"[Rr]eported|" +
        r"CVE|" +
        r"SVE" +
        r")" +
        r".*[:：]\s*"  # everything after userless words
    )
    res = re.sub(excess_words_regex, "", value)
    return res


def convert_to_timestamp(value):
    ret = None

    # samsung, lg
    if re.match(r"SMR-\w{3}-\d{4}", value):
        clear = re.sub("(SMR|-)", " ", value)
        ret = datetime.strptime(clear, "  %b %Y")
    # huawei
    if re.match(r".*EMUI/Magic UI", value):
        clear = re.sub(".*updates ", "", value)
        ret = datetime.strptime(clear, "%B %Y")
    if ret is None:
        return None

    return int(ret.timestamp())


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
        input_processor=MapCompose(remove_tags, get_cve_names)
    )
    header = scrapy.Field(
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
    timestamp = scrapy.Field(
        input_processor=MapCompose(remove_tags, convert_to_timestamp)
    )
    pass


class BulletArticle(BulletBase):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
    )
    pass
