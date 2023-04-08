import scrapy  # type: ignore
import logging
import socket
import time
import re
from json import loads
from scrapy.loader import ItemLoader
from scrapy.http import Request
from Bullet.items import BulletCVE


def is_valid(value):
    if value["id"] == "Android QuadRooter vulnerability":
        return False
    return True


class SamCVEScraper(scrapy.Spider):
    name = "LgCVE"

    def start_requests(self):
        url = "https://lgsecurity.lge.com:47901/psrt/bltns/selectBltnsAllSMR.do"
        yield Request(url,
                      dont_filter=True,
                      method="POST",
                      body='{"accessToken": "aa", "langCd": "en"}',
                      headers={'Content-Type': 'application/json'})

    def parse(self, response: scrapy.http.Response):
        """ This function parses a lg security bulletin

        @url https://lgsecurity.lge.com:47901/psrt/bltns/selectBltnsAllSMR.do
        @return items
        @scrapes bullet_title cve_id descr affected severity
        @scrapes url project spider server date
        """
        # TODO: add cache check
        # TODO: add existense check
        bullets = loads(response.body)["res"]
        for bullet in bullets:
            cnt = loads(bullet["contents"])
            for vuln in cnt["detail"]:
                if not is_valid(vuln):
                    continue

                item = ItemLoader(BulletCVE())
                item.add_value("bullet_title", cnt["title"])
                item.add_value("title", "LG Mobile Security")
                item.add_value("cve_id", vuln.get("id"))
                item.add_value("descr", vuln.get("Description"))
                item.add_value("severity", vuln.get("Severity"))
                item.add_value("affected", vuln.get("Affected Device Information"))
                item.add_value("affected", vuln.get("Affected Device information"))

                item.add_value("url", response.url)
                item.add_value("project", self.settings.get("BOT_NAME", "unknown"))
                item.add_value("spider", self.name)
                item.add_value("server", socket.gethostname())
                item.add_value("date", int(time.time()))

                i = item.load_item()
                self.log("%s - %s" % (i["cve_id"], i["title"]), logging.INFO)
                yield i
