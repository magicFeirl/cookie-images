from math import ceil

from app.crawler import BiliCrawler
from app.db import DrawTable
from config import MAX_CRAW_DRAW_PAGE, UID_LIST

crawler = BiliCrawler()

for uid in UID_LIST:
    last_page = ceil(DrawTable.table().count(poster_uid=uid) / 30)
    count = 0

    for page in range(MAX_CRAW_DRAW_PAGE):
        items = crawler.fetch_draw_doc_list(uid=uid, page_num=page) or []
        
        if items:
            count += len(items)
            print(items[0])
        
        DrawTable.insert_many(items)

        if not items or page == MAX_CRAW_DRAW_PAGE - 1:
            print(f"UID: {uid} 爬取完毕")
            print(f"uid={uid} 入库/更新 {count} 条数据")
            break


        print(f"Crawling {uid} no.{page} page data")
