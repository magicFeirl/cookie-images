import requests

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"

class Net(requests.Session):
    def __init__(self, base_url: str = "", **kwargs):
        super().__init__()

        self.base_url = base_url.rstrip("/")

        headers = kwargs.get("headers", {})
        if "user-agent" not in headers:
            headers["user-agent"] = DEFAULT_UA
        self.headers.update(headers)

    def request(self, method, url, **kwargs):
        if url.startswith("/") or not url.startswith("http"):
            url = self.base_url + "/" + url.lstrip("/")
        return super().request(method, url, **kwargs)
