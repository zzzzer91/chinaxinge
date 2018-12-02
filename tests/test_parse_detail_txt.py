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
        pass
