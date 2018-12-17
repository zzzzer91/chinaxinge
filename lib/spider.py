"""爬虫类。

Created：2018-8-28
Modified：2018-12-2
"""

import queue
import re
import threading
import atexit
from datetime import datetime

import pymysql
from lxml import etree

from lib import parser, log, sessions, db
from lib.types import *


class MultiThreadSpider(threading.Thread):

    headers: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    q: queue.Queue = queue.Queue()

    def __init__(self,
                 name: str,
                 mysql_config: MysqlConfig,
                 table_save: List[str],
                 daemon: bool = True) -> None:
        super().__init__(name=name, daemon=daemon)

        atexit.register(self.close)  # 注册清理函数，线程结束时自动调用

        self.mysql_conn = pymysql.connect(
            host=mysql_config['host'], port=mysql_config['port'],
            user=mysql_config['user'], password=mysql_config['pwd'],
            db=mysql_config['db'], autocommit=True
        )
        self.cursor = self.mysql_conn.cursor()

        self._running = True

        self.session = sessions.Session()
        self.session.headers.update(self.headers)

        self.table_save = table_save

        self.sql_insert: Optional[str] = None  # 在子类中构建

    def run(self) -> None:
        """抽象方法，由子类继承创建。"""

        raise NotImplementedError

    def save(self, item: PostDetailDict) -> None:
        if not self.sql_insert:
            self.sql_insert = 'INSERT INTO {{}} ({}) VALUES ({})'.format(
                ', '.join(item),
                ', '.join(f'%({k})s' for k in item)
            )
        # 一份数据，要存多个表
        for tb in self.table_save:
            try:
                self.cursor.execute(self.sql_insert.format(tb), item)
            except pymysql.IntegrityError:
                pass
            except pymysql.err.Warning:  # 过滤不合法 mysql 类型
                pass

    def terminate(self) -> None:
        self._running = False

    def close(self) -> None:
        self.session.close()
        self.cursor.close()
        self.mysql_conn.close()

    @classmethod
    def create_task_list(cls, mysql_config: MysqlConfig, sql: str) -> None:
        """
        从 MySQL 中读取任务，
        放入一个全局变量 `q` 队列中，
        供多个线程使用。
        """

        for row in db.read_data(mysql_config, sql):
            cls.q.put(row)


class MultiThreadPostListSpider(MultiThreadSpider):

    url_gp_temp: str = 'http://gdgp.chinaxinge.com/style/mo2/default.asp?gp_id='

    # 上一次抓取时间，用于过滤抓取过的文章
    last_fetch_time: Optional[datetime] = None

    def __init__(self,
                 name: str,
                 mysql_config: MysqlConfig,
                 table_save:  List[str],
                 daemon: bool = True) -> None:
        super().__init__(name, mysql_config, table_save, daemon)

    def run(self) -> None:

        log.logger.info(f'PostListSpider {self.name} 启动')

        while self._running:
            try:
                gp_id, gp_name = self.q.get(block=False)
            except queue.Empty:
                break
            url = self.url_gp_temp + gp_id
            r = self.session.get(url)
            self.session.cookies.clear()
            if not r:
                continue
            r.encoding = 'GBK'

            create_time = datetime.now()

            items: List[PostDetailDict] = []
            for item in parser.parse_gp_website(r.text, self.last_fetch_time):
                item['club_id'] = gp_id
                item['club'] = gp_name
                item['create_time'] = create_time
                item['flag'] = 1  # 默认 1
                items.append(item)
            if items:
                # 将更后面的日期排在前面，去重时保留更新的内容
                items.sort(key=lambda x: x['race_date'], reverse=True)
                for item in items:
                    log.logger.debug(str(item))
                    self.save(item)
        log.logger.info(f'PostListSpider {self.name} 结束')

    @classmethod
    def get_last_fetch_time(cls, mysql_config: MysqlConfig) -> None:
        mysql_sql = 'SELECT start_time from spider_work_time ORDER BY id DESC limit 1'
        cls.last_fetch_time = db.read_data(mysql_config, mysql_sql)[0][0]


class MultiThreadPostDetailSpider(MultiThreadSpider):

    def __init__(self,
                 name: str,
                 mysql_config: MysqlConfig,
                 table_save:  List[str],
                 daemon: bool = True) -> None:
        super().__init__(name, mysql_config, table_save, daemon)

    def run(self) -> None:

        log.logger.info(f'PostDetailSpider {self.name} 启动')

        while self._running:
            try:
                row = self.q.get(block=False)
            except queue.Empty:
                break

            url = row[0]
            club = row[1]
            race_id = row[2]
            race_name = row[3]
            race_date = row[4]
            kilo = row[5]
            _type = row[6]

            r = self.session.get(url)
            self.session.cookies.clear()
            if not r:
                continue

            self.sql_insert = None  # 因为 item 的 key 并不相同，所以要置 None

            create_time = datetime.now()

            # 根据 URL 选择对应解析方式
            if url.endswith('.htm'):
                parse = parser.parse_gp_post_htm
            elif url.endswith(('.txt', '.TXT')):
                parse = parser.parse_gp_post_txt
            elif url.rpartition('?')[0].endswith('.asp'):
                def parse(response):
                    response.encoding = 'utf-8'
                    selector = etree.HTML(r.text)
                    page_container = selector.xpath('.//a[text()="第末页"]/@href')
                    if page_container:
                        page_url = page_container[0]
                        page = int(re.findall(r'page=(\d+)', page_url)[0])
                        yield from parser.parse_gp_post_asp(response)
                        for i in range(2, page + 1):
                            next_url = f'{url}&page={i}'
                            r2 = self.session.get(next_url)
                            self.session.cookies.clear()
                            if not r:
                                continue
                            yield from parser.parse_gp_post_asp(r2)
                    else:
                        yield from parser.parse_gp_post_asp(response)
            else:
                log.logger.error('对应解析方式不存在！')
                exit(1)

            for item in parse(r):
                item['club'] = club
                item['race_id'] = race_id
                item['race_name'] = race_name
                item['race_date'] = race_date
                item['kilo'] = kilo
                item['type'] = _type
                item['create_time'] = create_time
                item['flag'] = 1  # 默认 1
                # log.logger.debug(str(item))
                self.save(item)

        log.logger.info(f'PostDetailSpider {self.name} 结束')


def run_multi_thread_spider(
        spider_class: Type[MultiThreadSpider],
        table_save:  List[str],
        thread_num: int,
        mysql_sql: str,
        mysql_config: MysqlConfig) -> None:
    """创建爬虫任务。

    :param spider_class: 爬虫类。
    :param table_save: 爬虫抓取数据后保存到的表。
    :param thread_num: 线程数量。
    :param mysql_sql: 创建任务队列，所执行的 mysql 语句。
    :param mysql_config: mysql 配置。
    """

    spider_class.create_task_list(
        mysql_config,
        mysql_sql
    )

    thread_list: List[MultiThreadSpider] = []
    for i in range(thread_num):
        t = spider_class(
            f'thread{i+1}', mysql_config, table_save
        )
        thread_list.append(t)

    for t in thread_list:
        t.start()
    try:
        for t in thread_list:
            t.join()
    except KeyboardInterrupt:  # 只有主线程能收到键盘中断
        for t in thread_list:  # 防止下面在保存完 `row` 后，线程又请求一个新 `row`
            t.terminate()
        exit(1)
