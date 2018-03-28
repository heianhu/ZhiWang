python3 crawl_url.py

if [ $? == 0 ];then
	cd apps/crawl_data/crawl_ZhiWang_Periodicals
	scrapy crawl crawl_detail
fi
