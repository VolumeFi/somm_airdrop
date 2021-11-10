import data_transforms
import pytest
import pandas as pd

class TestRevenueV2Factory:
    @pytest.fixture
    def factory(self) -> data_transforms.RevenueV2Factory:
        return data_transforms.RevenueV2Factory()

    def test_load_table(self, factory):
        assert factory.table is not None
        assert isinstance(factory.table, (pd.DataFrame))
        ...

class TestActionsPart1V2Factory:
    @pytest.fixture
    def factory(self) -> data_transforms.ActionsPart1V2Factory:
        return data_transforms.ActionsPart1V2Factory()

    def test_load_table(self, factory):
        assert factory.table is not None
        assert isinstance(factory.table, (pd.DataFrame))

class TestActionsPart2V2Factory:
    @pytest.fixture
    def factory(self) -> data_transforms.ActionsPart2V2Factory:
        return data_transforms.ActionsPart2V2Factory()

    def test_load_table(self, factory):
        assert factory.table is not None
        assert isinstance(factory.table, (pd.DataFrame))


