from typing import Any

import scrapy
import logging
import datetime
from scrapy.loader import ItemLoader
from other.items import BulletCVE


def is_valid(value):
    return True


class HuaweiCVEScraper(scrapy.Spider):
    name = "HuaweiCVE"
    domain = "consumer.huawei.com"
    link = "https://%s/en/support/bulletin/%d/%d"

    def start_requests(self):
        assert self.name[-3:] == "CVE", f"There is no CVE suffix: {self.name}"

        curr_year = datetime.datetime.now().year
        curr_month = datetime.datetime.now().month
        for y in range(2021, curr_year+1):
            for m in range(1, 12+1):
                if y == curr_year and m > curr_month:
                    continue
                url = self.link % (self.domain, y, m)
                yield scrapy.http.Request(url)

    def parse(self, response: scrapy.http.Response, **kwargs: Any) -> Any:
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
            item.add_value("timestamp", bullet_title)
            txt = vuln.get()
            item.add_value("cve_names", txt)
            item.add_value("header", txt)

            xpath = "following-sibling::p[%d]"
            item.add_xpath("description", xpath % 3)
            item.add_xpath("affected", xpath % 2)
            item.add_xpath("severity", xpath % 1)

            i = item.load_item()
            self.log("%s - %s" % (i["cve_names"], i["header"]), logging.INFO)
            yield i
