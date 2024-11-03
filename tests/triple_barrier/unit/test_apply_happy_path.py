from venv import logger

import pandas as pd

from tests.triple_barrier.integration.test_triple_barrier_apply_happy_path import OUTPUT_FOLDER
from triple_barrier.trading import DataSetLabeler
from triple_barrier.trade_labeling import TradeSide
from triple_barrier.trading import TradingParameters
import triple_barrier.constants as const

OUTPUT_FOLDER: str  = f"{const.ROOT_FOLDER}/tests/triple_barrier/integration/output/"


class TestTripleBarrierApply:
    """
    This set, tests the class and method that makes abstraction of
    apply execution on a pandas dataset,
    """

    def test_long(self,
                  prepare_price_data):

        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.BUY,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)
        trades: pd.DataFrame = dataset_labeler.compute()

        trades.to_parquet(f"{OUTPUT_FOLDER}/test-apply-long-no-dynamic-exit.parquet")

        for row in trades.iterrows():
            if row[1]["close-type"] == "time-expiration":
                assert row[1]["profit"] != 40 and row[1]["profit"] != 20
            elif row[1]["close-type"] == "stop-loss":
                assert row[1]["profit"] == -20.00
            else:
                assert row[1]["profit"] == 40.00


    def test_short(self,
                  prepare_price_data):

        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.SELL,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)

        trades: pd.DataFrame = dataset_labeler.compute()

        trades.to_parquet(f"{OUTPUT_FOLDER}/test-apply-short-no-dynamic-exit.parquet")

        for row in trades.iterrows():
            if row[1]["close-type"] == "time-expiration":
                assert row[1]["profit"] != 40 and row[1]["profit"] != 20
            elif row[1]["close-type"] == "stop-loss":
                assert row[1]["profit"] == -20.00
            else:
                assert row[1]["profit"] == 40.00
