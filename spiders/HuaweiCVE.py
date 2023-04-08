import scrapy  # type: ignore
import logging
import socket
import time
from scrapy.loader import ItemLoader
from Bullet.items import BulletCVE


class HuiCVEScraper(scrapy.Spider):
    name = "HuaweiCVE"
    # TODO: add last month check
    start_urls = [
        "https://consumer.huawei.com/en/support/bulletin/2023/4/"
    ]

    def parse(self, response: scrapy.http.Response):
        """ This function parses a huawei security bulletin

        @url https://consumer.huawei.com/en/support/bulletin
        @return items
        @scrapes cve_id title descr affected severity patch
        @scrapes url project spider server date
        """
        # TODO: add cache check
        # TODO: add existense check
        # TODO: add third-party library patches
        sel = "//div[contains(@class, safe-info-gxq)] \
                /p[                                   \
                   contains(@class, 'titile-size')    \
                   and starts-with(text(), 'CVE-')    \
                  ]"
        vulns = response.xpath(sel)
        for vuln in vulns:
            item = ItemLoader(BulletCVE(), vuln)
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
            self.log("%s - %s" % (i["cve_id"][0], i["title"][0]), logging.INFO)
            yield i
