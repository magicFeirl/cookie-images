from app.models.draw import DrawDocItem
from app.net import Net

BASE_URL = "https://api.bilibili.com"


class BiliCrawler(Net):
    def __init__(self):
        super().__init__(base_url=BASE_URL)

    def fetch_draw_doc_list(
        self,
        uid: int,
        page_num: int = 0,
    ) -> list[DrawDocItem]:

        params = {
            "uid": uid,
            "page_num": page_num,
            "page_size": 30,  # 后端固定为 30
        }

        url = "/x/dynamic/feed/draw/doc_list"
        response = self.get(BASE_URL + url, params=params).json()
        items = response["data"]["items"]

        if not items:
            return None

        return [
            DrawDocItem.model_validate(
                {
                    **item,
                    "pictures": [
                        p["img_src"] for p in (item["pictures"] or [{"img_src": []}])
                    ],
                    'dyn_id': str(item['dyn_id'])
                }
            )
            for item in items
        ]
