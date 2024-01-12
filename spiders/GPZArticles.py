from typing import Any

import scrapy
import logging
import datetime
import re
from scrapy.loader import ItemLoader
from other.items import BulletArticle


def is_valid(value):
    return True


class GPZArticlesScraper(scrapy.Spider):
    name = "GPZArticles"
    domain = "googleprojectzero.blogspot.com"
    link = "https://%s/?action=getTitles" +\
        "&widgetId=BlogArchive1" +\
        "&widgetType=BlogArchive" +\
        "&responseType=js" +\
        "&path=%s/%d"

    def start_requests(self):
        assert self.name[-8:] == "Articles", f"There is no Articles suffix: {self.name}"

        curr_year = datetime.datetime.now().year
        url = self.link % (self.domain, self.domain, curr_year)
        yield scrapy.http.Request(url)

    def parse(self, response: scrapy.http.Response, **kwargs: Any) -> Any:
        links = re.findall(r"'url':\s*'(https?:\/\/[^\s]+)'",
                           response.body.decode("utf8"))
        for link in links:
            if not is_valid(link):
                continue
            yield scrapy.http.Request(link, callback=self.parse_item)

    def parse_item(self, response: scrapy.http.Response):
        item = ItemLoader(BulletArticle(), response=response)
        item.add_xpath(
            "title", "//*[                               \
                          @itemprop='name' and           \
                          contains(@class, 'post-title') \
                         ]/text()")

        i = item.load_item()
        self.log("%s" % (i["title"]), logging.INFO)
        yield i
