import pandas as pd

from triple_barrier.trade_labeling import DataSetLabeler
from triple_barrier.trade_labeling import TradeSide
from triple_barrier.trading import TradingParameters


class TestTripleBarrierApply:
    """
    This set, tests the class and method that makes abstraction of
    apply execution on a pandas dataset,
    """

    def test_long(self, prepare_price_data):
        df = prepare_price_data

        dataset_labeler = DataSetLabeler(open=df.open_bid,
                                         high=df.high_bid,
                                         low=df.low_bid,
                                         close=df.close_bid)

        trade_params = TradingParameters(
            entry_column=df["entry"],
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.BUY,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )
        trades: pd.DataFrame = dataset_labeler.compute(trade_params


        )

        assert len(trades) == 10
        assert sum(trades["profit"]) == 1000

    def test_short(self, prepare_price_data):
        df = prepare_price_data
        dataset_labeler = DataSetLabeler()

        trades: pd.DataFrame = dataset_labeler.compute(
            open=df.open_bid,
            high=df.high_bid,
            low=df.low_bid,
            close=df.close_bid,
            entry_column="entry",
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.SELL,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )

        assert len(trades) == 10
        assert sum(trades["profit"]) == 1000