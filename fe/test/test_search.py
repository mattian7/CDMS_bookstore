import time

import pytest

from fe.access import search
from fe import conf


class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.title = "美丽心灵"
        self.store_id = "store_1"
        self.author = "[美] 西尔维娅·娜萨"
        self.tags = "纳什"
        self.subcontent = "狂人日记 & 孔乙己"
        self.mysearch = search.Search(conf.URL)
        yield
        # do after test

    def test_param_ok(self):
        code = self.mysearch.param_search(title=self.title, author=self.author, tags=self.tags)
        assert code == 200

        code = self.mysearch.param_search(title=self.title, author=self.author, tags=self.tags, store_id=self.store_id)
        assert code == 200

    def test_content_ok(self):
        code = self.mysearch.content_search(sub_content=self.subcontent)
        assert code == 200

        code = self.mysearch.content_search(sub_content=self.subcontent, store_id=self.store_id)
        assert code == 200
