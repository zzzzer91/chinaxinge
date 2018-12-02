from lib import spider, parser, log
from lib.types import *
from config import *

log.logger.set_log_level(log.DEBUG)


class TestSpider(spider.MultiThreadSpider):

    def __init__(self,
                 name: str,
                 mysql_config: MysqlConfig,
                 table_save: str,
                 daemon: bool=True) -> None:
        super().__init__(name, mysql_config, table_save, daemon)

    def run(self) -> None:

        log.logger.info(f'{self.name} 启动')

        # 通过
        # url = 'http://gdgp6.chinaxinge.com/shuju2/201806/201806130921588405.htm'
        # 通过
        # url = 'http://gdgp1.chinaxinge.com/shuju2/201706/2017651057418117.htm'
        # 通过
        # url = 'http://gdgp1.chinaxinge.com/shuju2/201809/2018921237111576.htm'
        # 通过
        # url = 'http://gdgp1.chinaxinge.com/shuju2/201612/201612281735521261.htm'
        # 通过
        # url = 'http://gdgp3.chinaxinge.com/shuju2/201611/2016111219213510841.htm'
        url = 'http://gdgp1.chinaxinge.com/shuju2/201809/201809302127179025.htm'
        url = 'http://gdgp1.chinaxinge.com/shuju2/201711/20171131717048037.htm'

        r = self.session.get(url)
        self.session.cookies.clear()
        if not r:
            return

        r.encoding = 'GBK'
        parser.parse_gp_post_txt(r.text)


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
