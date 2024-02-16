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
    return calculate_test_features()


def calculate_test_features() -> pd.DataFrame:

    file_name = f"{constants.ROOT_FOLDER}/tests/data/EURUSD_5 Mins_Ask_2023.01.02_2024.02.02.csv"

    columns = ["date-time", "open", "high", "low", "close", "volume"]
    price = pd.read_csv(file_name,
                        names=columns,
                        parse_dates=True,
                        index_col="date-time",
                        header=0)
    calculate_entry(price)
    calculate_exit(price)
    return price


def calculate_entry(price: pd.DataFrame):
    # calculate entry signal
    calculate_features(price)
    mask_signal = (price["mva-12"] > price["mva-24"]) & \
                    (price["mva-12"].shift(1) <= price["mva-24"].shift(1)) & \
                    (price["close"]> price["open"])
    price.loc[mask_signal, "entry-signal"] = 1
    price["entry"] = price["entry-signal"].shift(1)

    return price


def calculate_exit(price: pd.DataFrame):
    # calculate entry signal
    calculate_features(price)
    mask_signal = (price["mva-12"] < price["mva-24"]) & \
                    (price["mva-12"].shift(1) >= price["mva-24"].shift(1)) & \
                    (price["close"]< price["open"])
    price.loc[mask_signal, "exit-signal"] = 1
    price["exit"] = price["exit-signal"].shift(1)


def calculate_features(price: pd.DataFrame):
    price["mva-12"] = price["close"].rolling(12).mean().round(5)
    price["mva-24"] = price["close"].rolling(24).mean().round(5)


