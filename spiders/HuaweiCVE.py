import scrapy  # type: ignore
from Bullet.items import BulletItem


class HuiCVEScaper(scrapy.Spider):
    name = "HuaweiCVE"
    # TODO: add last month check
    start_urls = [
        "https://consumer.huawei.com/en/support/bulletin/2023/4/"
    ]

    def parse(self, response: scrapy.http.Response):
        # TODO: add cache check
        # TODO: add existense check
        # TODO: add third-party library patches
        bullet: scrapy.Selector = response.css("div.safe-info-gxq")
        vulns = bullet.xpath(".//p[contains(@class, 'titile-size') \
                                   and starts-with(text(), 'CVE-')]")
        for vuln in vulns:
            item = BulletItem()
            item["cve_id"] = vuln.css("::text").re_first(r"CVE-\d{4}-\d{4}")
            item["cust_id"] = None
            item["title"] = vuln.css("::text").get().split(":")[1].strip()
            item["links"] = None
            item["descr"] = vuln.xpath(
                "following-sibling::p[3]/text()"
            ).get().split(":")[1].strip()
            item["affected"] = vuln.xpath(
                "following-sibling::p[2]/text()"
            ).get().split(":")[1].strip()
            item["severity"] = vuln.xpath(
                "following-sibling::p[1]/text()"
            ).get().split(":")[1].strip()
            item["type"] = None
            item["patch"] = None
            yield item
