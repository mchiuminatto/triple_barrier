import pandas as pd
from triple_barrier.trade_labeling import (TradeSide,
                                           Labeler
                                           )
from triple_barrier.orders import Orders
from triple_barrier.types import OrderType
from triple_barrier import constants

DATA_FOLDER: str = f"{constants.ROOT_FOLDER}/tests/data/"
OUTPUT_FOLDER: str = f"{constants.ROOT_FOLDER}/tests/triple_barrier/integration/output/"
STOP_LOSS_PIPS: float = 5
TAKE_PROFIT_PIPS: float = 10
INSTRUMENT_PIP_POSITION = 4
TIME_LIMIT_PERIODS = 10


class TestApplyCases:
    def test_base_case_long(self, prepare_price_data):
        """
        Base case long:

        Long trade setup passing fix take profit, stop loss levels, and time barrier limit

        """
        df = prepare_price_data

        strategy_side = TradeSide.BUY

        entry: pd.DataFrame = df[(df.entry == 1)].copy(deep=True)
        entry = entry.apply(calculate_exit,
                            args=(df,
                                  STOP_LOSS_PIPS,
                                  TAKE_PROFIT_PIPS,
                                  strategy_side,
                                  INSTRUMENT_PIP_POSITION,
                                  TIME_LIMIT_PERIODS),
                            axis=1)

        entry["profit"] = (entry["close-price"] - entry["open"]) * 10 ** INSTRUMENT_PIP_POSITION
        grouped = entry.groupby("close-type")["profit"].sum()

        entry.to_parquet(f"{OUTPUT_FOLDER}base_case_long.parquet")

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)
        assert round(grouped[OrderType.DYNAMIC.value], 1) == -16.4
        assert round(grouped[OrderType.STOP_LOSS.value], 1) == -2345.0
        assert round(grouped[OrderType.TAKE_PROFIT.value], 1) == 1490.0
        assert round(grouped[OrderType.TIME_EXPIRATION.value], 1) == 678.7

    def test_issue_index_out_of_range(self):
        """
        Base case long:

        Case detected in a pipeline to build trading algorithms:

        Error reported
            IndexError: index 20 is out of bounds for axis 0 with size 19

        Parameters reported:

            take-profit: 100000
            stop-loss: 100000
            trade-side: Buy
            pip position: 4
            time-limit-periods : 20

        """
        df = pd.read_csv(f"{DATA_FOLDER}issue-index-out-of-range-dataset.csv",
                         index_col="date-time",
                         parse_dates=True)

        entry: pd.DataFrame = df
        entry = entry.apply(calculate_exit,
                            args=(df,
                                  100000,
                                  100000,
                                  TradeSide.BUY,
                                  4,
                                  20),
                            axis=1)

        entry["profit"] = (entry["close-price"] - entry["open_bid"]) * 10 ** INSTRUMENT_PIP_POSITION
        grouped = entry.groupby("close-type")["profit"].sum()

        entry.to_parquet(f"{OUTPUT_FOLDER}base_case_long.parquet")

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)
        assert round(grouped[OrderType.TIME_EXPIRATION.value], 1) == -2291.5

    def test_base_case_short(self, prepare_price_data_short):
        """
        Base case long:

        Long trade setup passing fix take profit, stop loss levels, and time barrier limit

        """
        df = prepare_price_data_short

        strategy_side = TradeSide.SELL

        entry: pd.DataFrame = df[(df.entry == 1)].copy(deep=True)
        entry = entry.apply(calculate_exit,
                            args=(df,
                                  STOP_LOSS_PIPS,
                                  TAKE_PROFIT_PIPS,
                                  strategy_side,
                                  INSTRUMENT_PIP_POSITION,
                                  TIME_LIMIT_PERIODS),
                            axis=1)

        entry["profit"] = (entry["open"] - entry["close-price"]) * 10 ** INSTRUMENT_PIP_POSITION
        grouped = entry.groupby("close-type")["profit"].sum()

        entry.to_parquet(f"{OUTPUT_FOLDER}base_case_short.parquet")

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)

        assert round(grouped[OrderType.DYNAMIC.value], 1) == -55.1
        assert round(grouped[OrderType.STOP_LOSS.value], 1) == -2410.0
        assert round(grouped[OrderType.TAKE_PROFIT.value], 1) == 1710.0
        assert round(grouped[OrderType.TIME_EXPIRATION.value], 1) == 694.0


def calculate_exit(row: any,
                   ohlc: pd.DataFrame,
                   stop_loss_width: float,
                   take_profit_width: float,
                   trade_side: TradeSide,
                   pip_decimal_position: int,
                   time_barrier_periods: int):
    try:
        box_setup = Orders()

        box_setup.open_time = str(row.name)
        box_setup.open_price = ohlc.loc[box_setup.open_time]["open_bid"]
        box_setup.take_profit_width = take_profit_width
        box_setup.stop_loss_width = stop_loss_width
        max_period_limit: int = min(time_barrier_periods, len(ohlc[box_setup.open_time:].index) - 1)

        box_setup.time_limit = ohlc[box_setup.open_time:].index[max_period_limit]
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=ohlc[ohlc.columns[0]],
                                  high_price=ohlc[ohlc.columns[1]],
                                  low_price=ohlc[ohlc.columns[2]],
                                  close_price=ohlc[ohlc.columns[3]],
                                  dynamic_exit=ohlc["exit"],
                                  box_setup=box_setup
                                  )
        barrier_builder.compute()

        row["close-price"] = barrier_builder.orders_hit.first_hit.level
        row["close-datetime"] = barrier_builder.orders_hit.first_hit.hit_datetime
        row["close-type"] = barrier_builder.orders_hit.first_hit.order_type.value

    except Exception as exp_instance:
        print(str(exp_instance))

    return row
