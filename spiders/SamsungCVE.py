import scrapy  # type: ignore
from BuLLet.items import BulletItem


class SamCVEScraper(scrapy.Spider):
    name = "SamsungCVE"
    start_urls = [
        "https://security.samsungmobile.com/securityUpdate.smsb"
    ]

    def parse(self, response: scrapy.http.Response):
        # TODO: add cache check
        # TODO: add existense check
        bullet: scrapy.Selector = response.css("div.acc_sub")[0]
        vulns = bullet.xpath(".//strong[font[starts-with(text(), 'SVE-')]]")
        for vuln in vulns:
            item = BulletItem()
            item["cve_id"] = vuln.css(
                "::text").re_first(r"CVE-\d{4}-\d{4}")
            item["cust_id"] = vuln.css(
                "::text").re_first(r"SVE-\d{4}-\d{4}")
            item["title"] = vuln.css("::text").get().split(":")[1].strip()
            item["links"] = None
            item["descr"] = vuln.xpath(
                "following-sibling::br[1]/following-sibling::text()[5]"
            ).get()
            item["affected"] = vuln.xpath(
                "following-sibling::br[1]/following-sibling::text()[2]"
            ).get().split(":")[1].strip()
            item["severity"] = vuln.xpath(
                "following-sibling::br[1]/following-sibling::text()[1]"
            ).get().split(":")[1].strip()
            item["type"] = None
            item["patch"] = vuln.xpath(
                "following-sibling::br[1]/following-sibling::text()[6]"
            ).get()
            yield item
