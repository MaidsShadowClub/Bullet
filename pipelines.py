# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import socket
import time

from Bullet import items
from Bullet import models

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem


class BulletAddMeta:
    def process_item(self, item, spider: scrapy.Spider):
        item["url"] = spider.url
        item["project"] = spider.settings.get("BOT_NAME", "unknown")
        item["spider"] = spider.name
        item["server"] = socket.gethostname()
        item["date"] = int(time.time())
        return item


class DefaultValuesPipeline:
    def process_item(self, item, _):
        for field in item.fields:
            item.setdefault(field, None)
        return item


class BulletSaveArticle:
    def __init__(self):
        engine = models.db_connect()
        models.create_table(engine)
        self.db = sessionmaker(bind=engine)()

    def is_dublicate(self, item):
        article = self.db.execute(
            select(models.Article)
            .where(models.Article.title == item["title"])
        ).first()

        if article is None:
            return False
        return True

    def process_item(self, item, spider: scrapy.Spider):
        if type(item) != items.BulletArticle:
            return item

        if self.is_dublicate(item):
            self.db.close()
            raise DropItem("Dublicate Article")

        article = models.Article(
            title=item["title"],
            url=item["url"],
            project=item["project"],
            spider=item["spider"],
            server=item["server"],
            date=item["date"]
        )

        self.db.add(article)
        self.db.commit()
        self.db.close()

        return item


class BulletSaveCVE:
    def __init__(self):
        engine = models.db_connect()
        models.create_table(engine)
        self.db = sessionmaker(bind=engine)()

    def get_vendor(self, item):
        if item["spider"][-3:] != "CVE":
            raise DropItem("There is no CVE suffix: " + item["spider"])

        spider_name = item["spider"][:-3]
        vendor = self.db.execute(
            select(models.Vendor)
            .where(models.Vendor.name == spider_name)
        ).first()

        if vendor is not None:
            return vendor[0]

        vendor = models.Vendor(name=spider_name)
        self.db.add(vendor)
        self.db.commit()
        return vendor

    def get_bullet(self, item, vendor):
        bullet = self.db.execute(
            select(models.Bulletin)
            .where(
                models.Bulletin.title == item["bullet_title"],
                models.Bulletin.vendor_id == vendor.id
            )
        ).first()

        if bullet is not None:
            return bullet[0]

        bullet = models.Bulletin(
            title=item["bullet_title"],
            vendor_id=vendor.id,
            timestamp=item["timestamp"]
        )
        self.db.add(bullet)
        self.db.commit()
        return bullet

    def get_cve_info(self, item, bullet):
        cve_info = self.db.execute(
            select(models.CVEInfo).where(
                models.CVEInfo.description == item["description"],
                models.CVEInfo.header == item["header"],
                models.CVEInfo.bulletin_id == bullet.id
            )
        ).first()

        if cve_info is None:
            cve_info = models.CVEInfo(
                bulletin_id=bullet.id,
                header=item["header"],
                links=item["links"],
                description=item["description"],
                affected=item["affected"],
                severity=item["severity"],
                weakness=item["weakness"],
                reported=item["reported"],
                patch=item["patch"],
                url=item["url"],
                project=item["project"],
                spider=item["spider"],
                server=item["server"],
                date=item["date"]
            )
            self.db.add(cve_info)
            self.db.commit()
        else:
            cve_info = cve_info[0]
        return cve_info

    def is_cve_dublicate(self, cve_name, bullet):
        # TODO: add refresh after 2 month for Android Bulletin
        row = self.db.execute(
            select(models.CVE).where(
                models.CVE.bulletin_id == bullet.id,
                models.CVE.name == cve_name
            )
        ).first()

        if row is None:
            return False
        return True

    def process_item(self, item, spider: scrapy.Spider):
        if type(item) != items.BulletCVE:
            return item

        vendor = self.get_vendor(item)
        bullet = self.get_bullet(item, vendor)
        cve_info = self.get_cve_info(item, bullet)

        for name in item["cve_names"]:
            if self.is_cve_dublicate(name, bullet):
                self.db.close()
                raise DropItem("Dublicate CVE")

            cve = models.CVE(
                name=name,
                bulletin_id=bullet.id,
                cve_info_id=cve_info.id,
            )
            self.db.add(cve)
            self.db.commit()
        self.db.close()

        return item
