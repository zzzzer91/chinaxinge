"""配置文件"""

# 线程数量
THREAD_NUM_POST_LIST = 1
THREAD_NUM_POST_DETAIL = 1


# MYSQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'pwd': 'xxx',
    'db': 'chinaxinge',
}

MYSQL_TABLE_READ_ID = 'gp_info'
MYSQL_TABLE_SAVE_POST = 'pigeon_max_race_before'
MYSQL_TABLE_SAVE_PIGEON = 'pigeon_race_before'
