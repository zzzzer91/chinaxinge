"""解析公棚主页文章标题。

Created：2018-8-28
Modified：2018-11-11
"""

import re
from datetime import datetime
import os

import jieba
from lxml import etree

from lib import log, keyword, env
from lib.types import *

jieba.load_userdict(os.path.join(env.DICT_PATH, 'title.txt'))


RE_TITLE_PARENTHESE: Pattern = re.compile(r'(.+)[（(【《][^）)】》]*[）)】》]?$')


def _split_post_title(title: str) -> str:
    """去掉标题最后的括号内容。"""

    result = RE_TITLE_PARENTHESE.match(title)
    if result:
        title = result.group(1)

    return title


RE_TITLE_KILOMETER: Pattern = re.compile(r'.*?(\d+)(km|KM|千米|公里).*')


def _extract_kilometer(title: str) -> Optional[int]:
    """提取标题中的 km 。"""

    result = RE_TITLE_KILOMETER.match(title)
    km: Optional[int] = None
    if result:
        km = int(result.group(1))

    return km


def _is_right_url(url: str) -> bool:
    """过滤不符合要求的 URL 。"""

    if not url.startswith('http'):
        return False

    # 可能后缀 ('.xls', '.doc', '.txt', '.xlsx', '.TXT', 'html', 'htm') 和 普通网页
    # if not url.endswith(('.txt', '.TXT')):
    # if not url.rpartition('?')[0].endswith('.asp'):
    if not url.endswith(('.txt', '.TXT', '.htm')) and \
            not url.rpartition('?')[0].endswith('.asp'):
        return False

    return True


def parse_gp_website(html: str, last_fetch_time: datetime) -> Iterator[PostDetailDict]:
    """解析公棚页文章索引。"""

    selector = etree.HTML(html)
    ul_container = selector.xpath(
        './/div[@class="content_center"]/div[@class="zxgk" and @style="text-align:left"]/ul'
    )

    for ul_element in ul_container:
        td_container = ul_element.xpath('./li//td')
        for td_element in td_container:
            title: str = td_element.xpath('./a/font/text()')[0].strip()
            new_title: str = _split_post_title(title)
            # 标题分词
            seg: FrozenSet[str] = frozenset(jieba.cut(new_title, HMM=False, cut_all=False))

            # 存在过滤词，直接 pass
            if seg & keyword.TITLE_ELIMINATE:
                continue

            url: str = td_element.xpath('./a/@href')[0]
            if not _is_right_url(url):
                continue

            # 过滤过期文章
            publish_time: str = td_element.xpath('./span/text()')[0].strip()
            dt = datetime.strptime(publish_time, '%Y-%m-%d')
            if dt < last_fetch_time:
                continue

            item: PostDetailDict = {
                'kilo': None,
                'race_date': dt  # 文章发布时间，作为比赛时间，有误差
            }

            if seg & keyword.TITLE_QINGPENG:
                item['type'] = 1
                item['kilo'] = _extract_kilometer(new_title)
            elif seg & keyword.TITLE_SHANGLONG:
                item['type'] = 2
                item['kilo'] = _extract_kilometer(new_title)
            # 满足任意两 group，则匹配成功
            elif ((seg & keyword.TITLE_GROUP1) and (seg & keyword.TITLE_GROUP2)) or \
                    ((seg & keyword.TITLE_GROUP1) and (seg & keyword.TITLE_GROUP3)) or \
                    ((seg & keyword.TITLE_GROUP2) and (seg & keyword.TITLE_GROUP3)):
                item['type'] = 3
                kilo = _extract_kilometer(new_title)
                if kilo is not None and kilo < 100:
                    continue
                item['kilo'] = kilo
            else:
                continue

            item['race_name'] = _split_post_title(new_title)  # 再去一次括号，因为可能出现连续括号
            item['post_name'] = title  # 原始文章标题
            item['url'] = url

            yield item


def test_split_post_tile() -> None:
    s = '长明公棚决赛500公里4日归巢【按会员号】'
    print(RE_TITLE_PARENTHESE.match(s).group(1))
    s = '金鑫第二关归巢清单《按编号排序》'
    print(RE_TITLE_PARENTHESE.match(s).group(1))


def test_jieba() -> None:
    s = '陕西威力秋棚第四站（六）公里训放汇总'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '阳帝珲公棚5月24日700公里加强赛前100名综合成绩'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '福建腾宇赛鸽中心2018年100公里清棚现场集鸽工作图片'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '淮安火车头公棚500公里决赛小团体名单'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '河北宏大翔威公棚550公里加站赛现场直播'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '宁夏国力：国力公棚70，120，200公里成绩对比 '
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '直播地址'
    print(jieba.lcut(s, HMM=False, cut_all=False))
    s = '赛鸽欣赏'
    print(jieba.lcut(s, HMM=False, cut_all=False))


if __name__ == '__main__':
    test_split_post_tile()
    test_jieba()
