#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu@live.com'

from pymysql import connect
import os
import codecs
from ZhiWang.mysettings import DATABASES
DATABASES = DATABASES['default']


class OperationDatabases(object):
    def __init__(self):
        self.mysql_conn = connect(
            host=DATABASES['HOST'], port=int(DATABASES['PORT']), database=DATABASES['NAME'],
            user=DATABASES['USER'], password=DATABASES['PASSWORD']
        )
        self.mysql_cursor = self.mysql_conn.cursor()

    def __del__(self):
        self.mysql_cursor.close()
        self.mysql_conn.close()

    def exec_mysql(self, sql, native=False):
        """
        将SQL传入impala中运行
        :param sql: SQL语句
        :param native: 是否为原始数据
        :return:
        """
        try:
            self.mysql_cursor.execute(sql)
            if native is False:
                fields = [x[0] for x in self.mysql_cursor.description]
                res = [dict(zip(fields, row)) for row in self.mysql_cursor.fetchall()]
                return res
            else:
                return self.mysql_cursor.fetchall()
        except Exception as e:
            print('='*10)
            print(sql)
            print(e)
            print('='*10)

    def get_data_from_file(self, file_name, extra_params=dict(), native=False):
        fpath = os.path.join(
            os.path.join(os.path.abspath(os.path.dirname(__file__))) + '/sql/' + file_name + '.sql'
        )
        sql = codecs.open(fpath, 'r', 'utf-8').read().format(**extra_params)
        # print(sql)
        res = self.exec_mysql(sql, native=native)
        return res

    def get_data_from_sql(self, sql, native=False):
        res = self.exec_mysql(sql, native=native)
        return res
