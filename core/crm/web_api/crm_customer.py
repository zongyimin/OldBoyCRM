#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'xuebk'
import logging
import json
from django.conf import settings
from django.utils.safestring import mark_safe
from time import sleep
import logging
logger = logging.getLogger(__name__)
from ..web_models.models import Customer
from django.db.models import Q

class PageInfo(object):

    def __init__(self, currentPage, totalItems, perItems=10, pageNum=11):
        try:
            currentPage = int(currentPage)
        except Exception, e:
            currentPage = 1

        self.__currentPage = currentPage
        self.__perItems = perItems
        self.__totalItems = totalItems
        self.__pageNum = pageNum

    @property
    def current_page(self):
        return self.__currentPage

    @property
    def total_items(self):
        return self.__totalItems

    @property
    def total_page(self):
        if not self.__totalItems:
            self.__totalItems = 0
        val = self.__totalItems/self.__perItems +1 if self.__totalItems % self.__perItems >0 else self.__totalItems/self.__perItems
        return val

    @property
    def page_num(self):
        return self.__pageNum

    @property
    def start(self):
        val = (self.__currentPage - 1) * self.__perItems
        return val

    @property
    def end(self):
        val = self.__currentPage * self.__perItems
        return val

    def pager(self,baseurl=None):
        '''
        page:当前页
        all_page_count: 总页数
        '''
        page_html = []
        page = self.current_page
        all_page_count = self.total_page
        total_items = self.total_items

        #首页
        first_html = "<li><a href='javascript:void(0)' onclick='ChangePage(1)'>首页</a></li>"
        page_html.append(first_html)

        #上一页
        if page <= 1:
            prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
        else:
            prev_html = "<li><a href='javascript:void(0)' onclick='ChangePage(%d)'>上一页</a></li>" % (page-1, )
        page_html.append(prev_html)

        #11个页码
        if all_page_count < 11:
            begin = 0
            end = all_page_count

        #总页数大于 11
        else:
            #
            if page<6:
                begin = 0
                end = 11
            else:
                if page + 6 > all_page_count:
                    begin = page - 6
                    end = all_page_count
                else:
                    begin = page - 6
                    end = page + 5

        for i in range(begin,end):
            #当前页
            if page == i+1:
                a_html = "<li class='active'><a href='javascript:void(0)' onclick='ChangePage(%d)'>%d</a></li>" % (i+1, i+1, )
            else:
                a_html = "<li><a href='javascript:void(0)' onclick='ChangePage(%d)'>%d</a></li>" % (i+1, i+1, )
            page_html.append(a_html)
        #下一页
        if page+1 > all_page_count:
            next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
        else:
            next_html = "<li><a href='javascript:void(0)' onclick='ChangePage(%d)' >下一页</a></li>" % (page+1, )

        page_html.append(next_html)
        #尾页
        end_html = "<li><a href='javascript:void(0)' onclick='ChangePage(%d)' >尾页</a></li>" % (all_page_count, )
        page_html.append(end_html)

        # 页码概要
        end_html = "<li><a href='javascript:void(0)' >共 %d页 / %d 条数据</a></li>" % (all_page_count,total_items, )
        page_html.append(end_html)

        #将列表中的元素拼接成页码字符串
        page_string = mark_safe(''.join(page_html))

        return page_string


class BaseResponse(object):
    def __init__(self):
        self.status = False
        self.message = ''
        self.data = None


def get_list_crm_customer(request, ret):
    response = BaseResponse()
    try:
        conditions = request.POST.get('search', None)
        conditions_key = request.POST.get('search_key', None)
        page = request.GET.get('page', None)
        if not conditions:
            conditions = "{}"
        if not conditions_key:
            conditions_key = "{}"
        conditions = json.loads(conditions)
        conditions_key = json.loads(conditions_key)
        logger.info("conditions:%s,conditions_key:%s,page:%s" % (conditions, conditions_key, page))
        all_count = get_describe_instances_count(conditions=conditions,conditions_key=conditions_key,status=["pending", "running", "stopped", "suspended"])
        page_info = PageInfo(page, all_count.count, perItems=settings.REST_FRAMEWORK['PAGE_SIZE'])
        ret['results'] = get_describe_instances(page_info.start, page_info.end, data=all_count.data).data
        ret["current_page"] = page_info.current_page
        ret["total_page"] = page_info.total_page
        ret["count"] = page_info.total_items
        ret['per_page'] = settings.REST_FRAMEWORK['PAGE_SIZE']
        ret['ret_code'] = 0
        response.status = True
    except Exception, e:
        logger.error(e.message)
        response.message = str(e)
    return ret


def get_describe_instances_count(conditions,conditions_key,**kwargs):
    """

    :param kwargs:
    :return:
    """
    response = BaseResponse()
    try:
        # create search condition
        con = Q()
        for k, v in conditions.items():
            temp = Q()
            temp.connector = 'OR'
            for item in v:
                temp.children.append((k, item))
            con.add(temp, 'AND')

        for k, v in conditions_key.items():
            k = k.split('.')[-1]
            temp = Q()
            temp.connector = 'AND'
            if v is None:
                continue
            if len(v) == 0:
                continue
            temp.children.append((k, v))
            con.add(temp, 'AND')
        print con
        data = Customer.objects.filter(con).values()
        response.count = len(data)
        response.data = data
        response.status = True
    except Exception, e:
        print e.message
        response.message = str(e)
    return response


def get_describe_instances(start, end, data, **kwargs):
    response = BaseResponse()
    try:
        data = data[start:end]
        for i in data:
            ret_instance_id(i)
        response.data = list(data)
        response.status = True
    except Exception, e:
        print e
        response.message = str(e)
    return response


def ret_instance_id(data):
    heihei = Customer.objects.get(id=data['id'])
    data['colored_status'] = heihei.colored_status()
    data['get_enrolled_course'] = heihei.get_enrolled_course()
    print data
    pass


def main():
    pass


if __name__ == '__main__':
    main()