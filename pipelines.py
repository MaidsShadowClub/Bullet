# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import socket
import time
import Bullet.items as items
import Bullet.models as bull_db

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
        engine = bull_db.db_connect()
        bull_db.create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider: scrapy.Spider):
        session = self.Session()

        if type(item) != items.BulletArticle:
            return item

        stmt = select(bull_db.Article).where(
            bull_db.Article.title == item["title"]
        )
        row = session.execute(stmt).first()
        if row is not None:
            session.close()
            raise DropItem("Dublicate Article")

        article = bull_db.Article(
            title=item["title"],
            url=item["url"],
            project=item["project"],
            spider=item["spider"],
            server=item["server"],
            date=item["date"]
        )

        session.add(article)
        session.commit()
        session.close()

        return item


class BulletSaveCVE:
    def __init__(self):
        engine = bull_db.db_connect()
        bull_db.create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider: scrapy.Spider):
        session = self.Session()

        if type(item) != items.BulletCVE:
            return item
        bullet = session.query(bull_db.Bulletin).filter_by(
            title=item["bullet_title"]
        ).first()
        if bullet is None:
            bullet = bull_db.Bulletin(
                title=item["bullet_title"]
            )
            session.add(bullet)
            session.commit()

        # check if cve_info exists
        stmt = select(bull_db.CVEInfo).where(
            bull_db.CVEInfo.description == item["description"],
            bull_db.CVEInfo.title == item["title"],
            bull_db.CVEInfo.bulletin_id == bullet.id
        )
        row = session.execute(stmt).first()

        if row is None:
            cve_info = bull_db.CVEInfo(
                bulletin_id=bullet.id,
                title=item["title"],
                links=item["links"],
                description=item["description"],
                affected=item["affected"],
                severity=item["severity"],
                type_info=item["type_info"],
                patch=item["patch"],
                url=item["url"],
                project=item["project"],
                spider=item["spider"],
                server=item["server"],
                date=item["date"]
            )
            session.add(cve_info)
            session.commit()
        else:
            cve_info = row[0]

        for name in item["cve_names"]:
            # TODO: add refresh after 2 month for Android Bulletin
            stmt = select(bull_db.CVE).where(
                bull_db.CVE.bulletin_id == bullet.id,
                bull_db.CVE.name == name
            )
            row = session.execute(stmt).first()
            if row is not None:
                session.close()
                raise DropItem("Dublicate CVE")

            cve = bull_db.CVE(
                name=name,
                bulletin_id=bullet.id,
                cve_info_id=cve_info.id,
            )
            session.add(cve)
            session.commit()

        session.close()

        return item
