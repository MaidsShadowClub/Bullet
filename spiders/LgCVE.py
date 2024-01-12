from typing import Any

import scrapy
import logging
from json import loads
from scrapy.loader import ItemLoader
from other.items import BulletCVE


def is_valid(value):
    if value["id"] == "Android QuadRooter vulnerability":
        return False
    return True


# key "affected device information" have two different cases
# so get_elem used
def get_elem(data, key):
    ret = []
    for k in iter(data):
        if key.lower() == k.lower():
            ret.append(data[k])
    return ret


class LgCVEScraper(scrapy.Spider):
    name = "LgCVE"
    domain = "lgsecurity.lge.com"
    link = "https://%s:47901/psrt/bltns/selectBltnsAllSMR.do"

    def start_requests(self):
        assert self.name[-3:] == "CVE", f"There is no CVE suffix: {self.name}"

        url = self.link % self.domain
        yield scrapy.http.Request(url,
                                  dont_filter=True,
                                  method="POST",
                                  body='{"accessToken": "aa", "langCd": "en"}',
                                  headers={'Content-Type': 'application/json'})

    def parse(self, response: scrapy.http.Response, **kwargs: Any) -> Any:
        bullets = loads(response.body)["res"]
        for bullet in bullets:
            cnt = loads(bullet["contents"])
            for vuln in cnt["detail"]:
                if not is_valid(vuln):
                    continue

                item = ItemLoader(BulletCVE())
                item.add_value("bullet_title", get_elem(bullet, "title"))
                item.add_value("timestamp", get_elem(bullet, "title"))
                item.add_value("header", "LG Mobile Security")
                item.add_value("cve_names", get_elem(vuln, "id"))
                item.add_value("description", get_elem(vuln, "description"))
                item.add_value("severity", get_elem(vuln, "severity"))
                item.add_value("reported", get_elem(vuln, "date reported"))
                item.add_value("affected", get_elem(vuln, "affected device information"))

                i = item.load_item()
                self.log("%s - %s" %
                         (i["cve_names"], i["header"]), logging.INFO)
                yield i
