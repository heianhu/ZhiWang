# ZhiWang
爬取、搜索、分析知网数据

### 主要功能
1. 爬取知网中A、B类期刊的的信息(不包括文章)
2. 做成搜索页面，在不登录的情况下能够搜索后单一查看，登陆后可以批量下载信息
3. 分析文章引用间关系(待完成)

### 使用方法
1. 在ZhiWang中新建一个mysetting.py文件，填入对应信息
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'heianhu'

SECRET_KEY = ''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}
```
2. 修改rootcorn

