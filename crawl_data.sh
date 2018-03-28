python3 crawl_url.py

if [ $? == 1 ];then
	python3 `pwd`'/apps/crawl_data/crawl_ZhiWang_Periodicals/debug_scrapy.py'
fi
