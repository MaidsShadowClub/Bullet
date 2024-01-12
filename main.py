from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import spiders
from other.database import Database


def main():
    db = Database()
    conn, curs = db.open()
    curs.execute(open("other/init_db.sql").read())
    conn.commit()
    db.close(conn, curs)

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spiders.AndroidCVEScraper)
    # process.crawl(spiders.GPZArticlesScraper)
    process.crawl(spiders.HuaweiCVEScraper)
    process.crawl(spiders.LgCVEScraper)
    process.crawl(spiders.SamsungCVEScraper)
    process.start()


if __name__ == "__main__":
    main()
