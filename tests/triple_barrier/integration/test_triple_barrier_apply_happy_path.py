import pandas as pd
from triple_barrier.trade_labeling import (TradeSide,
                                           Labeler
                                           )
from triple_barrier.orders import Orders
from triple_barrier.types import OrderType
from triple_barrier import constants

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
    box_setup = Orders()

    box_setup.open_time = str(row.name)
    box_setup.open_price = ohlc.loc[box_setup.open_time]["open"]
    box_setup.take_profit_width = take_profit_width
    box_setup.stop_loss_width = stop_loss_width
    box_setup.time_limit = ohlc[box_setup.open_time:].index[time_barrier_periods]
    box_setup.trade_side = trade_side
    box_setup.pip_decimal_position = pip_decimal_position

    barrier_builder = Labeler(open_price=ohlc.open,
                              high_price=ohlc.high,
                              low_price=ohlc.low,
                              close_price=ohlc.close,
                              dynamic_exit=ohlc["exit"],
                              box_setup=box_setup
                              )
    barrier_builder.compute()

    row["close-price"] = barrier_builder.orders_hit.first_hit.level
    row["close-datetime"] = barrier_builder.orders_hit.first_hit.hit_datetime
    row["close-type"] = barrier_builder.orders_hit.first_hit.order_type.value

    return row
