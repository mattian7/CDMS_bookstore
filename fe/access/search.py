import requests
from urllib.parse import urljoin


class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def param_search(self, title=None, author=None, tags=None, store_id=None) -> int:
        json = {"title": title, "author": author, "tags": tags, "store_id": store_id}
        url = urljoin(self.url_prefix, "param_search")
        r = requests.post(url, json=json)
        return r.status_code

    def content_search(self, sub_content: str, store_id=None):
        json = {"sub_content": sub_content, "store_id": store_id}
        url = urljoin(self.url_prefix, "content_search")
        r = requests.post(url, json=json)
        return r.status_code
