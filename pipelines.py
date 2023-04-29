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
        title = item["title"]

        query = select(models.Article).where(
            models.Article.title == title
        )
        article = self.db.execute(query).first()

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

        name = item["spider"][:-3]
        query = select(models.Vendor).where(
            models.Vendor.name == name
        )
        vendor = self.db.execute(query).first()

        if vendor is not None:
            return vendor[0]

        vendor = models.Vendor(name=name)
        self.db.add(vendor)
        self.db.commit()
        return vendor

    def get_bullet(self, item, vendor):
        id = vendor.id
        title = item["bullet_title"]
        timestamp = item["timestamp"]

        query = select(models.Bulletin).where(
            models.Bulletin.title == title,
            models.Bulletin.vendor_id == id
        )
        bullet = self.db.execute(query).first()

        if bullet is not None:
            return bullet[0]

        bullet = models.Bulletin(
            title=title,
            vendor_id=id,
            timestamp=timestamp
        )
        self.db.add(bullet)
        self.db.commit()
        return bullet

    def get_cve_info(self, item, bullet):
        id = bullet.id

        query = select(models.CVEInfo).where(
            models.CVEInfo.description == item["description"],
            models.CVEInfo.title == item["title"],
            models.CVEInfo.bulletin_id == id
        )
        row = self.db.execute(query).first()

        if row is None:
            cve_info = models.CVEInfo(
                bulletin_id=id,
                title=item["title"],
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
            cve_info = row[0]
        return cve_info

    def is_cve_dublicate(self, name, bullet):
        id = bullet.id

        # TODO: add refresh after 2 month for Android Bulletin
        query = select(models.CVE).where(
            models.CVE.bulletin_id == id,
            models.CVE.name == name
        )
        row = self.db.execute(query).first()

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
