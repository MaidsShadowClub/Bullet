import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship
from scrapy.utils.project import get_project_settings


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    creds = get_project_settings().get("MYSQL_CONNECTION")
    return sa.create_engine(creds)


def create_table(engine):
    Base.metadata.create_all(engine)


class SpiderInfo:
    url = sa.Column(sa.Text)
    project = sa.Column(sa.String(30))
    spider = sa.Column(sa.String(30))
    server = sa.Column(sa.String(30))
    date = sa.Column(sa.Integer)


class Article(Base, SpiderInfo):
    __tablename__ = "article"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)


class Bulletin(Base):
    __tablename__ = "bulletin"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)


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

    title = sa.Column(sa.Text)
    links = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    affected = sa.Column(sa.Text)
    severity = sa.Column(sa.Text)
    type_info = sa.Column(sa.Text)
    patch = sa.Column(sa.Text)
