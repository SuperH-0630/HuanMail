from flask import url_for
from typing import Optional


def get_max_page(count: int, count_page: int):
    """ 计算页码数 (共计count个元素, 每页count_page个元素) """
    res = (count // count_page) + (0 if count % count_page == 0 else 1)
    if res == 0:
        return 1
    return res


def get_page(url, page: int, count: int, **kwargs):
    """ 计算页码的按钮 """
    if count <= 9:
        page_list = [[i + 1, url_for(url, page=i + 1, **kwargs)] for i in range(count)]
    elif page <= 5:
        """
        [1][2][3][4][5][6][...][count - 1][count]
        """
        page_list = [[i + 1, url_for(url, page=i + 1)] for i in range(6)]
        page_list += [None,
                      [count - 1, url_for(url, page=count - 1, **kwargs)],
                      [count, url_for(url, page=count, **kwargs)]]
    elif page >= count - 5:
        """
        [1][2][...][count - 5][count - 4][count - 3][count - 2][count - 1][count]
        """
        page_list: Optional[list] = [[1, url_for(url, page=1, **kwargs)],
                                     [2, url_for(url, page=2, **kwargs)],
                                     None]
        page_list += [[count - 5 + i, url_for(url, page=count - 5 + i, **kwargs)] for i in range(6)]
    else:
        """
        [1][2][...][page - 2][page - 1][page][page + 1][page + 2][...][count - 1][count]
        """
        page_list: Optional[list] = [[1, url_for(url, page=1, **kwargs)],
                                     [2, url_for(url, page=2, **kwargs)],
                                     None]
        page_list += [[page - 2 + i, url_for(url, page=page - 2 + i, **kwargs)] for i in range(5)]
        page_list += [None,
                      [count - 1, url_for(url, page=count - 1, **kwargs)],
                      [count, url_for(url, page=count, **kwargs)]]
    return page_list
