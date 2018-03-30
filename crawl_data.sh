python3 crawl_url.py

if [ $? == 0 ];then
	cd apps/crawl_data/crawl_ZhiWang_Periodicals
	scrapy crawl repair_references
fi
