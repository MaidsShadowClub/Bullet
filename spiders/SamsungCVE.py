import scrapy  # type: ignore
import logging
import socket
import time
from scrapy.loader import ItemLoader
from Bullet.items import BulletCVE


class SamCVEScraper(scrapy.Spider):
    name = "SamsungCVE"
    start_urls = [
        "https://security.samsungmobile.com/securityUpdate.smsb"
    ]

    def parse(self, response: scrapy.http.Response):
        """ This function parses a samsung security bulletin

        @url https://security.samsungmobile.com/securityUpdate.smsb
        @return items
        @scrapes cve_id title descr affected severity patch
        @scrapes url project spider server date
        """
        # TODO: add cache check
        # TODO: add existense check
        sel = "//div[@class='acc_sub']            \
               //strong                           \
                /font[                            \
                      starts-with(text(), 'SVE-') \
                     ]"
        vulns: scrapy.Selector = response.xpath(sel)
        for vuln in vulns:
            item = ItemLoader(BulletCVE(), vuln)
            txt = vuln.get()
            item.add_value("cve_id", txt)
            item.add_value("title", txt)

            xpath = "../following-sibling::br[1]/following-sibling::text()[%d]"
            item.add_xpath("severity", xpath % 1)
            item.add_xpath("affected", xpath % 2)
            item.add_xpath("descr", xpath % 5)
            item.add_xpath("patch", xpath % 6)

            item.add_value("url", response.url)
            item.add_value("project", self.settings.get("BOT_NAME", "unknown"))
            item.add_value("spider", self.name)
            item.add_value("server", socket.gethostname())
            item.add_value("date", int(time.time()))

            i = item.load_item()
            self.log("%s - %s" % (i["cve_id"], i["title"]), logging.INFO)
            yield i
