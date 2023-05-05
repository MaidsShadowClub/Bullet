import enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine
from scrapy.utils.project import get_project_settings


#                                                                     ┌───────┐
#                                                                     │ Basic │
#                                                                     └───────┘

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings.
    Returns sqlalchemy engine instance
    """
    creds = get_project_settings().get("MYSQL_CONNECTION")
    return sa.create_engine("mysql"+creds)


def db_async_connect():
    """
    Performs database async connection using database settings.
    Returns sqlalchemy engine instance
    """
    creds = get_project_settings().get("MYSQL_CONNECTION")
    return create_async_engine("mysql+asyncmy"+creds)


def create_table(engine):
    Base.metadata.create_all(engine)


async def async_create_table(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class SpiderInfo:
    url = sa.Column(sa.Text)
    project = sa.Column(sa.String(30))
    spider = sa.Column(sa.String(30))
    server = sa.Column(sa.String(30))
    date = sa.Column(sa.Integer)


#                                                                  ┌──────────┐
#                                                                  │ Articles │
#                                                                  └──────────┘


class Article(Base, SpiderInfo):
    __tablename__ = "article"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)


#                                                        ┌────────────────────┐
#                                                        │ Security bulletins │
#                                                        └────────────────────┘

class Vendor(Base):
    __tablename__ = "vendor"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text)


class Bulletin(Base):
    __tablename__ = "bulletin"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)
    timestamp = sa.Column(sa.Integer)
    vendor = relationship("Vendor")
    vendor_id = sa.Column(sa.Integer, sa.ForeignKey("vendor.id"))


class CVE(Base):
    __tablename__ = "cve"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    bulletin = relationship("Bulletin")
    bulletin_id = sa.Column(sa.Integer, sa.ForeignKey("bulletin.id"))
    cve_info_id = sa.Column(sa.Integer, sa.ForeignKey("cve_info.id"))


class CVEInfo(Base, SpiderInfo):
    __tablename__ = "cve_info"

    id = sa.Column(sa.Integer, primary_key=True)
    aliases = relationship("CVE")
    bulletin = relationship("Bulletin")
    bulletin_id = sa.Column(sa.Integer, sa.ForeignKey("bulletin.id"))

    header = sa.Column(sa.Text)
    links = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    affected = sa.Column(sa.Text)
    severity = sa.Column(sa.Text)
    weakness = sa.Column(sa.Text)
    reported = sa.Column(sa.Text)
    patch = sa.Column(sa.Text)

#                                                                  ┌──────────┐
#                                                                  │ Telegram │
#                                                                  └──────────┘


class NewsType(enum.Enum):
    cve_vendor = enum.auto()
    article = enum.auto()
    # conference = enum.auto()


user_news_table = sa.Table(
    "user_news", Base.metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id")),
    sa.Column("news_id", sa.Integer, sa.ForeignKey("news.id")),
)


class News(Base):
    __tablename__ = "news"

    id = sa.Column(sa.Integer, primary_key=True)
    seen = sa.Column(sa.Boolean)
    news_type = sa.Column(sa.Enum(NewsType))
    users = relationship("User", secondary=user_news_table,
                         back_populates="news")
    __mapper_args__ = {
        "polymorphic_on": news_type,
        # "polymorphic_identity": NewsType.article
    }


class CVEVendorNews(News):
    __tablename__ = "cve_news"

    id = sa.Column(sa.Integer, sa.ForeignKey("news.id"), primary_key=True)
    vendor = relationship("Vendor")
    vendor_id = sa.Column(sa.Integer, sa.ForeignKey("vendor.id"))

    __mapper_args__ = {
        "polymorphic_identity": NewsType.cve_vendor
    }


class ArticleNews(News):
    __tablename__ = "article_news"

    id = sa.Column(sa.Integer, sa.ForeignKey("news.id"), primary_key=True)
    article = relationship("Article")
    article_id = sa.Column(sa.Integer, sa.ForeignKey("article.id"))

    __mapper_args__ = {
        "polymorphic_identity": NewsType.article
    }


class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    tg_id = sa.Column(sa.Integer)
    timezone = sa.Column(sa.Integer, default=0)
    news = relationship("News", secondary=user_news_table,
                        back_populates="users")
