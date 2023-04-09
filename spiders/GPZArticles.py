import scrapy  # type: ignore
import logging
import socket
import time
import datetime
import re
from scrapy.loader import ItemLoader
from Bullet.items import BulletArticle


def is_valid(value):  # stub
    return True


class GPZArticles(scrapy.Spider):
    name = "GPZArticles"

    def start_requests(self):
        url = "https://googleprojectzero.blogspot.com/" +\
            "?action=getTitles" +\
            "&widgetId=BlogArchive1" +\
            "&widgetType=BlogArchive" +\
            "&responseType=js" +\
            "&path=https://googleprojectzero.blogspot.com/%d"
        curr_year = datetime.datetime.now().year

        yield scrapy.http.Request(url % curr_year,
                                  dont_filter=True,
                                  callback=self.parse)

    def parse(self, response: scrapy.http.Response):
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

        item.add_value("url", response.url)
        item.add_value("project", self.settings.get("BOT_NAME", "unknown"))
        item.add_value("spider", self.name)
        item.add_value("server", socket.gethostname())
        item.add_value("date", int(time.time()))

        i = item.load_item()
        self.log("%s - %s" % (i["title"], i["url"]), logging.INFO)
        yield i
