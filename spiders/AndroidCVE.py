from typing import Any

import scrapy
import logging
import re
from scrapy.loader import ItemLoader
from other.items import BulletCVE


def is_valid(value):
    return True


mapping = {"CVE": "cve_names", "References": "links", "Severity": "severity", "Component": "component",
           "Type": "weakness", "Updated AOSP versions": "affected", "Updated versions": "affected",
           "Bug(s) with AOSP links": "links", "Affected versions": "affected", "Date reported": "reported",
           "Updated Google devices": "affected", "CVEs": "cve_names", "Subcomponent": "component", "Bug(s) ": "links",
           "Severity*": "severity", "Researchers": "Skip", "Updated Nexus devices": "Skip",
           "Updated kernel versions": "affected"}


def get_tables(response: scrapy.http.Response):
    info = response.xpath("//table[tbody/tr/th[contains(text(), 'CVE')]]")
    if info:
        return info

    info = response.xpath("//table[tr/th[contains(text(), 'CVE')]]")
    if info:
        return info

    info = response.xpath("//table[thead/tr/th[contains(text(), 'CVE')]]")
    if info:
        return info

    if response.url in [
        "https://source.android.com/docs/security/bulletin/pixel/2018-10-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-02-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-03-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-04-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-05-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-06-01",
        "https://source.android.com/docs/security/bulletin/pixel/2019-07-01",
        "https://source.android.com/docs/security/bulletin/pixel/2020-10-01"
    ]:
        return []

    assert False, "No tables found"


def get_rows(table):
    info = table.xpath("tr")
    if info:
        return info

    info = table.xpath("tbody/tr")
    if info:
        return info

    assert False, "No rows found"


class AndroidCVEScraper(scrapy.Spider):
    name = "AndroidCVE"
    domain = "source.android.com"
    link = "https://%s/docs/security/bulletin"

    def start_requests(self):
        assert self.name[-3:] == "CVE", f"There is no CVE suffix: {self.name}"
        yield scrapy.http.Request(self.link % self.domain)

    def parse(self, response: scrapy.http.Response, **kwargs: Any) -> Any:
        links = response.xpath("//a[starts-with(@href, '/docs/security/bulletin/')]/@href")
        for link in links:
            raw_link = link.re_first(r"^\/docs\/security\/bulletin\/(android[-\d\w]*|(pixel\/)?\d{4}-\d{2}-\d{2})$")
            if not raw_link:
                continue
            url = "https://" + self.domain + "/docs/security/bulletin/" + raw_link
            yield scrapy.http.Request(url, callback=self.parse_bulletin)

    def parse_bulletin(self, response: scrapy.http.Response):
        tables = get_tables(response)
        for table in tables:
            head = table.xpath("preceding-sibling::h3[1]").get()

            rows = get_rows(table)
            db_columns = []
            for header in rows[0].xpath("th/text()"):
                db_columns.append(mapping[header.get()])
            # Filter all tables that don't contain CVE at first column
            if db_columns[0] != "cve_names":
                continue

            for cve_row in rows[1:]:
                # To handle case of multiple rows for CVE
                # like https://source.android.com/docs/security/bulletin/2015-12-01
                cve_arr = cve_row.xpath("td")
                if len(cve_arr) != len(db_columns):
                    continue

                item = ItemLoader(BulletCVE(), response=response)
                item.add_xpath("bullet_title", "//h1")
                item.add_xpath("timestamp", "//em[starts-with(text(), 'Published ')]/text()")
                item.add_value("header", head)
                for i in range(len(db_columns)):
                    if db_columns[i] == "Skip":
                        continue
                    value = cve_arr[i].get()
                    clear = re.sub(r"^(<td[^>]*>|\n| )*|(</td>|\n| )*$", "", value)
                    item.add_value(db_columns[i], clear)
                i = item.load_item()
                self.log("%s - %s" % (i["cve_names"], i["header"]), logging.INFO)
                yield i
