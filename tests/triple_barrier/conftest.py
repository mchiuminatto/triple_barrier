import pytest

import logging
import pandas as pd

from triple_barrier import constants



@pytest.fixture
def prepare_price_data() -> pd.DataFrame:

    file_name = f"{constants.ROOT_FOLDER}/tests/data/EURUSD_5 Mins_Ask_2023.01.02_2024.02.02.csv"

    columns = ["date-time", "open", "high", "low", "close", "volume"]
    price = pd.read_csv(file_name,
                        names=columns,
                        parse_dates=True,
                        index_col="date-time",
                        header=0)
    
    
    # calculate entry signal
    price["mva-12"] = price["close"].rolling(12).mean().round(5)
    price["mva-24"] = price["close"].rolling(24).mean().round(5)
    mask_signal = (price["mva-12"] > price["mva-24"]) & \
                    (price["mva-12"].shift(1) <= price["mva-24"].shift(1)) & \
                    (price["close"]> price["open"])
    price.loc[mask_signal, "signal"] = 1
    price["entry"] = price["signal"].shift(1)

    return price


@pytest.fixture
def prepare_entry_data(prepare_price_data):
    
    df = prepare_price_data
    
    entry_mark = df["entry"] == 1
    df_entry = df[entry_mark].copy(deep=True)
    
    return df_entry

