import pytest

import logging
import pandas as pd

from triple_barrier import constants


@pytest.fixture
def prepare_entry_data(prepare_price_data):
    df = prepare_price_data

    entry_mark = df["entry"] == 1
    df_entry = df[entry_mark].copy(deep=True)

    return df_entry


@pytest.fixture
def prepare_price_data() -> pd.DataFrame:
    return calculate_test_features_long()


def prepare_price_data_short() -> pd.DataFrame:
    return calculate_test_features_short()


def calculate_test_features_long() -> pd.DataFrame:

    file_name = f"{constants.ROOT_FOLDER}/tests/data/EURUSD_5 Mins_Ask_2023.01.02_2024.02.02.csv"

    columns = ["date-time", "open", "high", "low", "close", "volume"]
    price = pd.read_csv(file_name,
                        names=columns,
                        parse_dates=True,
                        index_col="date-time",
                        header=0)
    calculate_long_signal(price, "entry")
    calculate_short_signal(price, "exit")

    return price


def calculate_test_features_short() -> pd.DataFrame:

    file_name = f"{constants.ROOT_FOLDER}/tests/data/EURUSD_5 Mins_Ask_2023.01.02_2024.02.02.csv"

    columns = ["date-time", "open", "high", "low", "close", "volume"]
    price = pd.read_csv(file_name,
                        names=columns,
                        parse_dates=True,
                        index_col="date-time",
                        header=0)

    calculate_short_signal(price, "entry")
    calculate_long_signal(price, "exit")

    return price


def calculate_long_signal(price: pd.DataFrame, output_col_name: str):
    # calculate entry signal
    calculate_features(price)
    mask_signal = (price["mva-12"] > price["mva-24"]) & \
                    (price["mva-12"].shift(1) <= price["mva-24"].shift(1)) & \
                    (price["close"]> price["open"])
    price.loc[mask_signal, "entry-signal"] = 1
    price[output_col_name] = price["entry-signal"].shift(1)

    return price


def calculate_short_signal(price: pd.DataFrame, output_col_name: str):
    # calculate entry signal
    calculate_features(price)
    mask_signal = (price["mva-12"] < price["mva-24"]) & \
                    (price["mva-12"].shift(1) >= price["mva-24"].shift(1)) & \
                    (price["close"] < price["open"])
    price.loc[mask_signal, "exit-signal"] = 1
    price[output_col_name] = price["exit-signal"].shift(1)


def calculate_features(price: pd.DataFrame):
    price["mva-12"] = price["close"].rolling(12).mean().round(5)
    price["mva-24"] = price["close"].rolling(24).mean().round(5)


