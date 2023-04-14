import scrapy  # type: ignore
import logging
import datetime
from scrapy.loader import ItemLoader
from Bullet.items import BulletCVE


def is_valid(value):
    return True


class SamCVEScraper(scrapy.Spider):
    name = "SamsungCVE"
    domain = "security.samsungmobile.com"
    link = "https://%s/securityUpdate.smsb"

    def start_requests(self):
        self.url = self.link % self.domain
        curr_year = datetime.datetime.now().year
        headers = {
            'Content-Type':
            'application/x-www-form-urlencoded'
        }
        for i in range(2015, curr_year+1):
            yield scrapy.http.Request(self.url,
                                      method="POST",
                                      headers=headers,
                                      body="year=%d" % i,
                                      )

    def parse(self, response: scrapy.http.Response):
        """ This function parses a samsung security bulletin

        @url https://security.samsungmobile.com/securityUpdate.smsb
        @scrapes cve_names title description affected severity patch
        @return items
        """
        # TODO: add cache check
        # TODO: add existense check
        vulns: scrapy.Selector
        bullet_title: scrapy.Selector

        bullet_titles = response.xpath("//div[@class='acc_title']")
        for bullet_title in bullet_titles:
            if not is_valid(bullet_title):
                continue

            sel = "following-sibling::div[1]" +\
                "//strong" +\
                "/font[starts-with(text(), 'SVE-')]"
            vulns = bullet_title.xpath(sel)
            for vuln in vulns:
                item = ItemLoader(BulletCVE(), vuln)
                item.add_value("bullet_title", bullet_title.get())
                txt = vuln.get()
                item.add_value("cve_names", txt)
                item.add_value("title", txt)

                xpath = ".." +\
                        "/following-sibling::br[1]" +\
                        "/following-sibling::text()[%d]"
                item.add_xpath("severity", xpath % 1)
                item.add_xpath("affected", xpath % 2)
                item.add_xpath("description", xpath % 5)
                item.add_xpath("patch", xpath % 6)

                i = item.load_item()
                self.log("%s - %s" %
                         (i["cve_names"], i["title"]), logging.INFO)
                yield i
