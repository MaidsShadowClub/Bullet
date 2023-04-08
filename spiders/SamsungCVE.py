import scrapy  # type: ignore
import logging
import socket
import datetime
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
        @scrapes cve_id cust_id title descr affected severity pathc
        @scrapes url project spider server date
        """
        # TODO: add cache check
        # TODO: add existense check
        vulns: scrapy.Selector = response.xpath(
            "//div[@class='acc_sub']//strong/font[starts-with(text(), 'SVE-')]")
        for vuln in vulns:
            item = ItemLoader(BulletCVE(), response=response)
            txt = vuln.get()
            item.add_value("cve_id", txt)
            item.add_value("cust_id", txt)
            item.add_value("title", txt)

            xpath = "../following-sibling::br[1]/following-sibling::text()"
            item.add_xpath("severity", f"{xpath}[1]")
            item.add_xpath("affected", f"{xpath}[2]")
            item.add_xpath("descr", f"{xpath}[5]")
            item.add_xpath("patch", f"{xpath}[6]")

            item.add_value("url", response.url)
            item.add_value("project", self.settings.get("BOT_NAME", "unknown"))
            item.add_value("spider", self.name)
            item.add_value("server", socket.gethostname())
            item.add_value("date", datetime.datetime.now())

            i = item.load_item()
            print(i)
            #self.log("%s - %s" % (i["cve_id"], i["title"]), logging.INFO)
            yield i
