"""抓取 chinaxinge 网各公棚带有指定关键字文章。

Created：2018-8-28
Modified：2018-12-2
"""

import warnings
from datetime import datetime

from lib import spider, log, db

from config import *

warnings.filterwarnings('error')  # 将警告提升为异常

# log.logger.set_log_level(log.DEBUG)


def insert_start_time() -> int:
    """保存爬虫的开始时间到 work_time 表中。"""

    item = {'start_time': datetime.now()}
    mysql_sql = 'INSERT INTO spider_work_time ({}) VALUES ({})'.format(
        ', '.join(item),
        ', '.join(f'%({k})s' for k in item)
    )

    return db.insert_data(MYSQL_CONFIG, mysql_sql, item)


def insert_end_time(work_time_id: int) -> None:
    """保存爬虫的结束时间到 work_time 表中。"""

    item = {'end_time': datetime.now()}
    mysql_sql = 'UPDATE spider_work_time SET {} WHERE {}'.format(
        ', '.join(f'{k} = %({k})s' for k in item),
        f'id = {work_time_id}'
    )

    db.insert_data(MYSQL_CONFIG, mysql_sql, item)


def main() -> None:

    # 抓取文章列表
    mysql_sql = 'SELECT gp_id, name FROM {}'.format(MYSQL_TABLE_READ_ID)
    spider.run_multi_thread_spider(spider.MultiThreadPostListSpider,
                                   MYSQL_TABLE_SAVE_POST,
                                   THREAD_NUM_POST_LIST,
                                   mysql_sql,
                                   MYSQL_CONFIG)
    # 这行必须放在 MultiThreadPostListSpider 后面，因为 start_time 会被先创建
    work_time_id = insert_start_time()

    # 抓取文章列表中文章细节
    mysql_sql = 'SELECT url, club, id, race_name, race_date, kilo, type FROM {}'.\
        format(MYSQL_TABLE_SAVE_POST[0])
    spider.run_multi_thread_spider(spider.MultiThreadPostDetailSpider,
                                   MYSQL_TABLE_SAVE_PIGEON,
                                   THREAD_NUM_POST_DETAIL,
                                   mysql_sql,
                                   MYSQL_CONFIG)

    insert_end_time(work_time_id)


if __name__ == '__main__':
    main()
