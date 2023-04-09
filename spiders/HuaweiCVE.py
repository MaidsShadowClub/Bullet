import scrapy  # type: ignore
import logging
import socket
import time
import datetime
from scrapy.loader import ItemLoader
from Bullet.items import BulletCVE


def is_valid(value):
    return True


class HuiCVEScraper(scrapy.Spider):
    name = "HuaweiCVE"

    def start_requests(self):
        url = "https://consumer.huawei.com/en/support/bulletin/%d/%d/"
        curr_year = datetime.datetime.now().year
        curr_month = datetime.datetime.now().month
        for y in range(2021, curr_year+1):
            for m in range(1, 12+1):
                if y == curr_year and m > curr_month:
                    continue
                link = url % (y, m)
                yield scrapy.http.Request(link)

    def parse(self, response: scrapy.http.Response):
        """ This function parses a huawei security bulletin

        @url https://consumer.huawei.com/en/support/bulletin
        @scrapes cve_id title descr affected severity patch
        @scrapes url project spider server date
        @return items
        """
        # TODO: add cache check
        # TODO: add existense check
        # TODO: add third-party library patches
        bullet_title = response.xpath("//h2[@class='safe-info-title']").get()
        sel = "//div[contains(@class, safe-info-gxq)] \
                /p[                                   \
                   contains(@class, 'titile-size')    \
                   and starts-with(text(), 'CVE-')    \
                  ]"
        vulns = response.xpath(sel)
        for vuln in vulns:
            item = ItemLoader(BulletCVE(), vuln)
            item.add_value("bullet_title", bullet_title)
            txt = vuln.get()
            item.add_value("cve_id", txt)
            item.add_value("title", txt)

            xpath = "following-sibling::p[%d]"
            item.add_xpath("descr", xpath % 3)
            item.add_xpath("affected", xpath % 2)
            item.add_xpath("severity", xpath % 1)

            item.add_value("url", response.url)
            item.add_value("project", self.settings.get("BOT_NAME", "unknown"))
            item.add_value("spider", self.name)
            item.add_value("server", socket.gethostname())
            item.add_value("date", int(time.time()))

            i = item.load_item()
            self.log("%s - %s" % (i["cve_id"], i["title"]), logging.INFO)
            yield i
