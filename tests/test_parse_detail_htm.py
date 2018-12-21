from lib import spider, parser, log
from lib.types import *
from config import *

log.logger.set_log_level(log.DEBUG)


class TestSpider(spider.MultiThreadSpider):

    def __init__(self,
                 name: str,
                 mysql_config: MysqlConfig,
                 table_save: List[str],
                 daemon: bool = True) -> None:
        super().__init__(name, mysql_config, table_save, daemon)

    def run(self) -> None:
        url = 'http://gdgp3.chinaxinge.com/shuju2/201812/201812061916569566.htm'
        r = self.session.get(url)
        if not r:
            return
        for item in parser.parse_gp_post_htm(r):
            log.logger.info(item)


def test() -> None:

    t = TestSpider(
        '1',
        MYSQL_CONFIG,
        MYSQL_TABLE_SAVE_PIGEON
    )
    t.start()
    t.join()


if __name__ == '__main__':
    test()
