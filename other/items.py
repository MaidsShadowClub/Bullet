# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from itemloaders.processors import MapCompose, Join, TakeFirst
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
            r".*" +  # everything before useless words
            r"(" +
            r"[Ii]mpact|" +
            r"[Ss]everity|" +
            r"[Aa]ffected|" +
            r"[Rr]eported|" +
            r"CVE|" +
            r"SVE" +
            r")" +
            r".*[:：]\s*"  # everything after useless words
    )
    res = re.sub(excess_words_regex, "", value)
    return res


def convert_to_timestamp(value):
    # samsung, lg
    if re.match(r"SMR-\w{3}-\d{4}", value):
        clear = re.sub("(SMR|-)", " ", value)
        ret = datetime.strptime(clear, "  %b %Y")
    # huawei
    elif re.match(r".*EMUI/Magic UI", value):
        clear = re.sub(".*updates ", "", value)
        ret = datetime.strptime(clear, "%B %Y")
    # android
    elif re.match(r"Published .*", value):
        clear = re.sub(r"Published\s*|(?<=\d{4})(.*)", "", value)
        ret = datetime.strptime(clear, "%B %d, %Y")
    else:
        return None

    return int(ret.timestamp())


class BulletBase(scrapy.Item):
    spider = scrapy.Field()


class BulletCVE(BulletBase):
    bullet_title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
        output_processor=Join(),
    )
    cve_names = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_cve_names),
    )
    header = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon, format_text),
        output_processor=Join(),
    )
    description = scrapy.Field(
        input_processor=MapCompose(clean_before_semicolon, format_text),
        output_processor=Join(),
    )
    affected = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon, format_text),
        output_processor=Join(),
    )
    severity = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon, format_text),
        output_processor=Join(),
    )
    reported = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_before_semicolon, format_text),
        output_processor=Join(),
    )
    weakness = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
        output_processor=Join(),
    )
    patch = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
        output_processor=Join(),
    )
    links = scrapy.Field(
        output_processor=Join(),
    )
    timestamp = scrapy.Field(
        input_processor=MapCompose(remove_tags, convert_to_timestamp),
        output_processor=TakeFirst(),
    )
    component = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
        output_processor=Join(),
    )
    pass


class BulletArticle(BulletBase):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_text),
    )
    pass
