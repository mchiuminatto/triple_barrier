import pytest
import pandas as pd

from tests.test_utils.dummy_strategy import calculate_test_features_long
from tests.test_utils.dummy_strategy import calculate_test_features_short


@pytest.fixture
def prepare_entry_data(prepare_price_data):
    df = prepare_price_data

    entry_mark = df["entry"] == 1
    df_entry = df[entry_mark].copy(deep=True)

    return df_entry


@pytest.fixture
def prepare_price_data() -> pd.DataFrame:
    return calculate_test_features_long()


@pytest.fixture
def prepare_price_data_short() -> pd.DataFrame:
    return calculate_test_features_short()



