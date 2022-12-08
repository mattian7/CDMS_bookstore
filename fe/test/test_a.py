import pytest
import time

class TestLazyLoad:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        time.sleep(60)
        yield
        # do after test

    def test_ok(self):
        pass