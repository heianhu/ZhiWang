#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu@live.com'

import zipfile
from dbsetting import OperationDatabases
import time


def write_to_txt(getdetailinfo_id):
    """
    将指定id的文章写入txt
    :param getdetailinfo_id: 文章summary中的id号
    :return: 生成的excel文件名(文章detail中的detail_id),失败时返回None
    """
    # 在Excel中插入数据，文件名为detail_id字段

    fields = ['FN', 'VR', 'PT', 'AU', 'AF', 'BA', 'CA', 'GP', 'BE', 'TI', 'SO', 'SE', 'BS', 'LA', 'DT',
              'CT', 'CY', 'CL', 'SP', 'HO', 'DE', 'ID', 'AB', 'C1', 'RP', 'EM', 'FU', 'FX', 'CR', 'NR',
              'TC', 'Z9', 'PU', 'PI', 'PA', 'SN', 'BN', 'J9', 'JI', 'PD', 'PY', 'VL', 'IS', 'SI', 'PN',
              'SU', 'BP', 'EP', 'AR', 'DI', 'D2', 'PG', 'P2', 'WC', 'SC', 'GA', 'UT', 'ER', 'EF']

    import collections

    values = collections.OrderedDict()
    values = values.fromkeys(fields)

    for k in values.keys():
        values[k] = list()

    # values = {field: [i, ] for i, field in enumerate(fields)}
    article_summary = OperationDatabases().get_data_from_file('find_summary',
                                                              extra_params={'summary_id': getdetailinfo_id})[0]
    article_detail = OperationDatabases().get_data_from_file('find_detail',
                                                             extra_params={
                                                                 'detail_id': article_summary.get('detail_id', [])})[0]
    if type(article_detail) is not dict:
        print('部分summary没有detail', getdetailinfo_id)
        return None

    # 文件名
    values['FN'].append(article_detail['detail_id'])
    # 作者
    # values['AU'][1] = article_summary.authors
    for author in article_detail['authors'].split():
        if author.isdigit():
            values['AU'].append(
                OperationDatabases().get_data_from_file(
                    'find_authors', extra_params={'author_id': author})[0]['authors_name']
            )
        else:
            values['AU'].append(author)
    # 标题
    values['TI'].append(article_summary['title'])
    # 出版日期
    values['PD'].append(article_summary['issuing_time'].strftime('%Y/%m/%d'))
    # issn号
    periodical = OperationDatabases().get_data_from_file(
        'find_periodicals', extra_params={'periodical_id': article_summary['source_id']})[0]
    values['SN'].append(periodical['issn_number'])
    # 出版物名称
    values['SO'].append(periodical['name'])
    # 摘要
    values['AB'].append('\n' + article_detail['detail_abstract'])

    # 关键词
    kw = article_detail['detail_keywords']
    # '' kw.split()
    # kw = [i.join('""') for i in kw.split()]
    kw = ';'.join(kw.split())
    values['DE'].append(kw)

    # 组织
    orgs = article_detail['organizations'].split()
    for org in orgs:
        if org.isdigit():
            values['C1'].append(
                OperationDatabases().get_data_from_file(
                    'find_organization', extra_params={'organization_id': org})[0]['organization_name']
            )
        else:
            values['C1'].append(org)

    # 参考文献
    article_reference = OperationDatabases().get_data_from_file(
        'find_references', extra_params={
            'references_id': article_detail['references_id'] if article_detail['references_id'] else 'null'
        })

    if article_reference:
        article_reference = article_reference[0]
        str_refer = ['CBBD', 'CDFD', 'CJFQ', 'CMFD', 'CRLDENG', 'SSJD', 'CCND', 'CPFD']
        refers = []  # 参考于各个期刊的id，每个期刊的id以列表形式存在 [[1,2],[3,4]]
        for refer in str_refer:
            refers.append(article_reference[refer].split())

        all_refers = list()
        for index, ref_db in enumerate(str_refer):
            all_refers.extend(
                OperationDatabases().get_data_from_file(
                    'find_references_detail', extra_params={
                        'ref_db': ref_db, 'ids': ','.join(refers[index]) if len(refers[index]) > 0 else 'null'
                    }
                )
            )
        for refers in all_refers:
            try:
                temp_refers_info = (
                refers['title'], ' ', refers['authors'], ' ', refers['source'], ' ', refers['issuing_time'])
            except KeyError:
                temp_refers_info = (refers['title'], ' ', refers['info'], ' ', refers['issuing_time'])
            values['CR'].append(temp_refers_info)

    filename = '{0}.txt'.format(article_detail['detail_id'])

    with open('download_txt/' + filename, 'w+', encoding='utf-8') as file:
        for key, all_value in values.items():
            file.write(str(key))
            for num, v in enumerate(all_value):
                if num != 0:
                    file.write('    ' + ''.join(v))
                else:
                    file.write('  ' + ''.join(v))

                if num != len(all_value) - 1:
                    file.write('\n')
            file.write('\n')

    return filename


# def compress_txt(ids):
#     """
#     将批量id的文章写入txt，然后压缩成一个zip文件
#     :param ids: summary文章id列表
#     :return: 生成的zip文件名(不包含路径)
#     """
#     files = []
#     zip_name = time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.zip'
#     jungle_zip = zipfile.ZipFile('download_txt/{0}'.format(zip_name), 'w')
#
#     for id in ids:
#         filename = write_to_txt(id)
#         file = BASE_DIR + 'download_txt/{0}'.format(filename)
#         jungle_zip.write(file, filename, compress_type=zipfile.ZIP_DEFLATED)
#
#     jungle_zip.close()
#
#     return zip_name

def download_all():
    all_id = OperationDatabases().get_data_from_sql("""
    SELECT
        id
    FROM crawl_data_summary
    """, native=True)
    for i in all_id:
        write_to_txt(i[0])


if __name__ == '__main__':
    download_all()
