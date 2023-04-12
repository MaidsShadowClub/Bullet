import scrapy  # type: ignore
import logging
import datetime
import re
from scrapy.loader import ItemLoader
from Bullet.items import BulletArticle


def is_valid(value):  # stub
    return True


class GPZArticles(scrapy.Spider):
    name = "GPZArticles"

    def start_requests(self):
        curr_year = datetime.datetime.now().year
        self.url = ("{domain}/" +
                    "?action=getTitles" +
                    "&widgetId=BlogArchive1" +
                    "&widgetType=BlogArchive" +
                    "&responseType=js" +
                    "&path={domain}/{year}").format(
            domain="https://googleprojectzero.blogspot.com",
            year=curr_year)

        yield scrapy.http.Request(self.url)

    def parse(self, response: scrapy.http.Response):
        """ This function parses a links from archive of blogspot.com

        @url https://googleprojectzero.blogspot.com/?action=getTitles&widgetId=BlogArchive1&widgetType=BlogArchive&responseType=js&path=https://googleprojectzero.blogspot.com/2023
        @returns requests 1
        """
        links = re.findall(r"'url':\s*'(https?:\/\/[^\s]+)'",
                           response.body.decode("utf8"))
        for link in links:
            if not is_valid(link):
                continue
            yield scrapy.http.Request(link, callback=self.parse_item)

    def parse_item(self, response: scrapy.http.Response):
        """ This function parses an articles from blogspot.com

        @url https://googleprojectzero.blogspot.com/2023/03/multiple-internet-to-baseband-remote-rce.html
        @scrapes title
        @returns items 1
        """
        item = ItemLoader(BulletArticle(), response=response)
        item.add_xpath(
            "title", "//*[                               \
                          @itemprop='name' and           \
                          contains(@class, 'post-title') \
                         ]/text()")

        i = item.load_item()
        self.log("%s" % (i["title"]), logging.INFO)
        yield i
