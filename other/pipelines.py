# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

import scrapy
from itemadapter import ItemAdapter
from scrapy.utils.defer import maybe_deferred_to_future

from other import items
from other.database import Database


class BulletAddMeta:
    @staticmethod
    def process_item(item, spider: scrapy.spiders.Spider):
        item["spider"] = spider.name
        return item


class AddDescriptionForCVE:
    SPLASH_URL = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}"

    async def process_item(self, item, spider: scrapy.spiders.Spider):
        adapter = ItemAdapter(item)
        if adapter.get("description"):
            return item

        cve_names = adapter["cve_names"]
        if not cve_names:
            return item
        name = ""
        for cve_name in cve_names:
            if cve_name.startswith("CVE-"):
                name = cve_name
                break

        if name == "":
            return item

        url = self.SPLASH_URL.format(cve_names[0])
        req = scrapy.Request(url, callback=scrapy.http.request.NO_CALLBACK)

        resp: scrapy.http.Response = await maybe_deferred_to_future(
            spider.crawler.engine.download(req)
        )

        if resp.status != 200:
            # Error happened, return item.
            return item

        query = "//table/tr[th[contains(text(), 'Description')]]/following-sibling::tr/td"
        descr = resp.xpath(query).get()
        clear = re.sub(r"^(<td[^>]*>|\n| )*|(</td>|\n| )*$", "", descr)

        adapter["description"] = clear
        return item


class DefaultValuesPipeline:
    @staticmethod
    def process_item(item, _):
        for field in item.fields:
            item.setdefault(field, "None")
        return item


class BulletSaveArticle:
    pass


#     def __init__(self):
#         self.db = database.Database()
#
#     async def is_dublicate(self, item):
#         article = await execute_query(self.conn,
#                                       "SELECT * FROM article WHERE title=$1", item["title"]
#                                       )
#
#         if article is None:
#             return False
#         return True
#
#     async def process_item(self, item, _):
#         if type(item) != items.BulletArticle:
#             return item
#
#         if self.is_dublicate(item):
#             self.db.close()
#             raise DropItem("Dublicate Article")
#
#         article = models.Article(
#             title=item["title"],
#             url=item["url"],
#             project=item["project"],
#             spider=item["spider"],
#             server=item["server"],
#             date=item["date"]
#         )
#
#         self.db.add(article)
#         self.db.commit()
#         self.db.close()
#
#         return item


class BulletSaveCVE:
    def __init__(self):
        db = Database()
        self.conn, self.curs = db.open()

    async def get_vendor(self, item) -> int:
        spider_name = item["spider"][:-3]
        self.curs.execute("SELECT id FROM vendor WHERE name=%s", (spider_name,))
        vendor_id = self.curs.fetchone()

        if not vendor_id:
            self.curs.execute("INSERT INTO vendor(name) VALUES (%s)", (spider_name,))
            self.conn.commit()
            self.curs.execute("SELECT id FROM vendor WHERE name=%s", (spider_name,))
            vendor_id = self.curs.fetchone()

        return vendor_id[0]

    async def get_bullet(self, item, vendor_id: int) -> int:
        self.curs.execute(
            f"SELECT id FROM bulletin WHERE title=%s AND vendor_id={vendor_id}", (item["bullet_title"],)
        )
        bullet_id = self.curs.fetchone()

        if not bullet_id:
            self.curs.execute(f"INSERT INTO bulletin(title, vendor_id, timestamp) "
                              f"VALUES (%s, {vendor_id}, to_timestamp({item['timestamp']}))", (item["bullet_title"],))
            self.conn.commit()

            self.curs.execute(
                f"SELECT id FROM bulletin WHERE title=%s AND vendor_id={vendor_id}", (item["bullet_title"],)
            )
            bullet_id = self.curs.fetchone()

        return bullet_id[0]

    async def get_cve_info(self, item):
        is_new = False
        self.curs.execute(
            f"SELECT id FROM cve_info "
            f"WHERE header=%s AND links=%s AND description=%s AND affected=%s "
            f"AND severity=%s AND weakness=%s AND reported=%s AND patch=%s AND spider=%s AND component=%s",
            (item["header"], item["links"], item["description"], item["affected"],
             item["severity"], item["weakness"], item["reported"], item["patch"], item["spider"], item["component"])
        )
        cve_info_id = self.curs.fetchone()

        if not cve_info_id:
            is_new = True
            self.curs.execute(f"INSERT INTO cve_info(header, links, description, affected, severity, "
                              f"weakness, reported, patch, spider, component) "
                              f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                              (item["header"], item["links"], item["description"], item["affected"], item["severity"],
                               item["weakness"], item["reported"], item["patch"], item["spider"], item["component"],))
            self.conn.commit()

            self.curs.execute(
                f"SELECT id FROM cve_info "
                f"WHERE header=%s AND links=%s AND description=%s AND affected=%s "
                f"AND severity=%s AND weakness=%s AND reported=%s AND patch=%s AND spider=%s AND component=%s",
                (item["header"], item["links"], item["description"], item["affected"],
                 item["severity"], item["weakness"], item["reported"], item["patch"], item["spider"], item["component"])
            )
            cve_info_id = self.curs.fetchone()

        return is_new, cve_info_id[0]

    async def process_item(self, item, _):
        if not isinstance(item, items.BulletCVE):
            return item

        vendor_id = await self.get_vendor(item)
        bullet_id = await self.get_bullet(item, vendor_id)
        is_new, cve_info_id = await self.get_cve_info(item)

        if not is_new:
            return item

        # TODO: if cve exists send notif
        for name in item["cve_names"]:
            self.curs.execute(f"INSERT INTO cve(name, bulletin_id) VALUES (%s, {bullet_id})", (name,))
            self.conn.commit()

            self.curs.execute(f"SELECT id FROM cve WHERE name=%s AND bulletin_id={bullet_id}", (name,))
            cve_id = self.curs.fetchone()[0]

            self.curs.execute(f"INSERT INTO cve_info_cve(cve_id, cve_info_id) VALUES ({cve_id}, {cve_info_id})")
            self.conn.commit()

        return item

    def close_spider(self, _):
        self.curs.close()
        self.conn.close()
