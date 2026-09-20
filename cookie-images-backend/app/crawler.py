from models.draw import DrawDocItem
from net import Net

BASE_URL = "https://api.bilibili.com"


class BiliCrawler(Net):
    def __init__(self):
        super().__init__(base_url=BASE_URL)

    def fetch_draw_doc_list(
        self, uid: int, page_num: int = 0, page_size: int = 20
    ) -> list[DrawDocItem]:

        params = {
            "uid": uid,
            "page_num": page_num,
            "page_size": page_size,
        }

        url = "/x/dynamic/feed/draw/doc_list"
        response = self.get(BASE_URL + url, params=params).json()
        items = response["data"]["items"]

        if not items:
            return []

        return [
            DrawDocItem.model_validate(
                {
                    **item,
                    "pictures": [p["img_src"] for p in item["pictures"]],
                }
            )
            for item in items
        ]
