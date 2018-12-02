"""解析文章内容。

Created：2018-8-28
Modified：2018-11-12
"""

import re

import cchardet
from lxml import etree
from requests import Response

from lib import log, keyword
from lib.types import *


def _get_col_index_core(td_list: List[str]) -> Dict[str, int]:
    """判断列索引必须字段，足环号和鸽主姓名。"""

    d_row_index = {}

    for i, col in enumerate(td_list):
        if col in keyword.COL_NUMBER:
            d_row_index['ring_number'] = i
        elif col in keyword.COL_NAME:
            d_row_index['name'] = i
        if len(d_row_index) == keyword.COL_COUNT_MUST:  # 已经满足必须列数量
            break
    else:
        raise IndexError
    return d_row_index


def _get_col_index_extra(td_list: List[str]) -> Dict[str, int]:
    """判断列索引额外字段。"""

    d_row_index = {}

    for i, col in enumerate(td_list):
        if col in keyword.COL_TIME:
            d_row_index['back_time'] = i
        elif col in keyword.COL_SPEED:
            d_row_index['speed'] = i
        elif col in keyword.COL_FEATHER:
            d_row_index['feather'] = i
        elif col in keyword.COL_AREA:
            d_row_index['area'] = i
        elif col in keyword.COL_NO:
            d_row_index['no'] = i
    return d_row_index


def _parse_htm(html: str) -> Iterator[PostDetailDict]:

    selector = etree.HTML(html)

    tr_container = selector.xpath('.//table[1]//tr')

    # 探测存在的列
    row_index = 0  # 存储行索引
    for tr_ele in tr_container[:20]:  # 扫描开头 20 行，匹配列名
        td_list: List[str] = []
        for e in tr_ele.xpath('./td'):
            text = e.xpath('string(.)')
            text = ''.join(text.split())
            # 如果节点文字为空，会返回 None
            td_list.append(text)

        log.logger.debug(str(td_list))

        try:
            d_row_index = _get_col_index_core(td_list)
            break
        except IndexError:
            pass
        row_index += 1
    else:  # 循环完整执行，代表没有匹配到列名
        return

    d_row_index.update(_get_col_index_extra(td_list))

    log.logger.debug(str(d_row_index))

    # 解析实际内容
    for tr_ele in tr_container[row_index+1:]:
        td_list = []
        for e in tr_ele.xpath('./td'):
            text = e.xpath('string(.)')
            # 如果节点文字为空，会返回 None
            td_list.append(text)

        item: PostDetailDict = {}
        try:
            for k, v in d_row_index.items():
                item[k] = td_list[v].strip().strip('#')
        except IndexError:
            log.logger.debug('行匹配错误')
            return

        # 如果有任意 value 为空，则结束
        if not all(item.values()):
            return

        yield item


def parse_gp_post_htm(r: Response) -> Iterator[PostDetailDict]:
    """解析 .htm 结尾的公棚的文章详情。"""

    for code in ['GBK', 'UTF-8']:  # 探测编码
        r.encoding = code
        i = 0
        for item in _parse_htm(r.text):
            i += 1
            yield item
        if i != 0:
            break


def _parse_asp(html: str) -> Iterator[PostDetailDict]:

    selector = etree.HTML(html)

    tr_container = selector.xpath('.//div//table[@bgcolor="#dddddd"]/tr')

    # 探测存在的列
    row_index = 0  # 存储行索引
    for tr_ele in tr_container[:20]:  # 扫描开头 20 行，匹配列名
        td_list: List[str] = []
        for e in tr_ele.xpath('./td'):
            text = e.xpath('string(.)')
            text = ''.join(text.split())
            # 如果节点文字为空，会返回 None
            td_list.append(text)

        log.logger.debug(str(td_list))

        try:
            d_row_index = _get_col_index_core(td_list)
            break
        except IndexError:
            pass
        row_index += 1
    else:  # 循环完整执行，代表没有匹配到列名
        return

    d_row_index.update(_get_col_index_extra(td_list))

    log.logger.debug(str(d_row_index))

    # 解析实际内容
    for tr_ele in tr_container[row_index+1:]:
        td_list = []
        for e in tr_ele.xpath('./td'):
            text = e.xpath('string(.)')
            # 如果节点文字为空，会返回 None
            td_list.append(text)

        item: PostDetailDict = {}
        try:
            for k, v in d_row_index.items():
                item[k] = td_list[v].strip().strip('#')
        except IndexError:
            log.logger.debug('行匹配错误')
            return

        # 如果有任意 value 为空，则结束
        if not all(item.values()):
            return

        yield item


def parse_gp_post_asp(r: Response) -> Iterator[PostDetailDict]:
    """解析 .asp 结尾的公棚的文章详情。"""

    r.encoding = 'utf-8'
    yield from _parse_asp(r.text)


RE_TEXT_LINE: Pattern = re.compile(r'[ ]{2,}|[ ]*[\t]+[ ]*')


def _parse_txt(txt: str) -> Iterator[PostDetailDict]:

    lines = txt.split('\r\n')

    # 探测存在的列
    row_index = 0  # 存储行索引
    for line in lines[:20]:  # 扫描开头 20 行，匹配列名
        td_list = line.split()
        log.logger.debug(str(td_list))
        try:
            d_row_index = _get_col_index_core(td_list)
            break
        except IndexError:
            pass
        row_index += 1
    else:  # 循环完整执行，代表没有匹配到列名
        return

    d_row_index.update(_get_col_index_extra(td_list))

    log.logger.debug(str(d_row_index))

    # 解析实际内容
    for line in lines[row_index+1:]:
        td_list = RE_TEXT_LINE.split(line.strip())

        item: PostDetailDict = {}
        try:
            for k, v in d_row_index.items():
                item[k] = td_list[v].strip().strip('#')
        except IndexError:
            log.logger.debug('行匹配错误 >>> %s' % str(td_list))
            continue

        yield item


def parse_gp_post_txt(r: Response) -> Iterator[PostDetailDict]:
    """解析 .txt 结尾的公棚的文章详情。"""

    r.encoding = cchardet.detect(r.content)['encoding']
    yield from _parse_txt(r.text)


def test() -> None:
    s = '           1	CHN 2018-01-0019527	393-7	            高保红	              雨花白	北京	6D7B38E1DC	2018-10-17 12:32:51.000             '
    print(RE_TEXT_LINE.split(s.strip()))


if __name__ == '__main__':
    test()
