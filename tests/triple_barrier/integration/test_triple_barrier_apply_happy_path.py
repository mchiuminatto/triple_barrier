import pandas as pd
from triple_barrier.triple_barrier import (TradeSide,
                                           MultiBarrierBuilder
                                           )
from triple_barrier import constants

OUTPUT_FOLDER: str = f"{constants.ROOT_FOLDER}/tests/triple_barrier/integration/output/"


class TestApplyCases:
    def test_base_case_long(self, prepare_price_data):
        """
        Base case long:

        Long trade setup passing fix take profit, stop loss levels, and time barrier limit

        """
        df = prepare_price_data

        def calculate_exit(row: any,
                           ohlc: pd.DataFrame,
                           stop_loss_width: float,
                           take_profit_width: float,
                           trade_side: TradeSide,
                           pip_decimal_position: int,
                           time_barrier_periods: int):
            barrier_builder = MultiBarrierBuilder(open_price=ohlc.open,
                                                  high_price=ohlc.high,
                                                  low_price=ohlc.low,
                                                  close_price=ohlc.close,
                                                  trade_open_datetime=str(row.name),
                                                  stop_loss_pips=stop_loss_width,
                                                  take_profit_pips=take_profit_width,
                                                  trade_side=trade_side,
                                                  pip_decimal_position=pip_decimal_position,
                                                  time_barrier_periods=time_barrier_periods,
                                                  dynamic_exit=ohlc.exit)
            barrier_builder.compute()

            row["close-price"] = barrier_builder.multi_barrier.first_hit.level
            row["close-datetime"] = barrier_builder.multi_barrier.first_hit.hit_datetime
            row["close-type"] = barrier_builder.multi_barrier.first_hit.barrier_type.value

            return row

        stop_loss_pips = 5
        take_profit_pips = 10
        strategy_side = TradeSide.BUY
        instrument_pip_position = 4
        time_limit_periods = 10
        pip_factor = 10 ** 4

        entry: pd.DataFrame = df[(df.entry == 1)].copy(deep=True)
        entry = entry.apply(calculate_exit,
                            args=(entry,
                                  stop_loss_pips,
                                  take_profit_pips,
                                  strategy_side,
                                  instrument_pip_position,
                                  time_limit_periods),
                            axis=1)

        mask_take_profit_hits = entry["close-type"] == "take-profit"
        sum_take_profit_hits = (
                                       entry[mask_take_profit_hits]["close-price"] - entry[mask_take_profit_hits][
                                   "open"]).sum() * pip_factor

        mask_stop_loss_hits = entry["close-type"] == "stop-loss"
        sum_stop_loss_hits = (
                                     entry[mask_stop_loss_hits]["close-price"] - entry[mask_stop_loss_hits][
                                 "open"]).sum() * pip_factor

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)
        assert round(sum_take_profit_hits, 0) == 4870
        assert round(sum_stop_loss_hits, 0) == -3110

        entry.to_parquet(f"{OUTPUT_FOLDER}base_case_long.parquet")

    def test_base_case_short(self, prepare_price_data):
        """

        Base case short

        Short trade setup passing fix take profit, stop loss levels, and time barrier limit

        """
        df = prepare_price_data

        def calculate_exit(row: any,
                           ohlc: pd.DataFrame,
                           stop_loss_width: float,
                           take_profit_width: float,
                           trade_side: TradeSide,
                           pip_decimal_position: int,
                           time_barrier_periods: int):
            barrier_builder = MultiBarrierBuilder(open_price=ohlc.open,
                                                  high_price=ohlc.high,
                                                  low_price=ohlc.low,
                                                  close_price=ohlc.close,
                                                  trade_open_datetime=str(row.name),
                                                  stop_loss_pips=stop_loss_width,
                                                  take_profit_pips=take_profit_width,
                                                  trade_side=trade_side,
                                                  pip_decimal_position=pip_decimal_position,
                                                  time_barrier_periods=time_barrier_periods,
                                                  dynamic_exit=ohlc.exit)
            barrier_builder.compute()

            row["close-price"] = barrier_builder.multi_barrier.first_hit.level
            row["close-datetime"] = barrier_builder.multi_barrier.first_hit.hit_datetime
            row["close-type"] = barrier_builder.multi_barrier.first_hit.barrier_type.value

            return row

        stop_loss_pips = 5
        take_profit_pips = 10
        strategy_side = TradeSide.SELL
        instrument_pip_position = 4
        time_limit_periods = 10
        pip_factor = 10 ** 4

        entry: pd.DataFrame = df[(df.entry == 1)].copy(deep=True)
        entry = entry.apply(calculate_exit,
                            args=(entry,
                                  stop_loss_pips,
                                  take_profit_pips,
                                  strategy_side,
                                  instrument_pip_position,
                                  time_limit_periods),
                            axis=1)

        mask_take_profit_hits = entry["close-type"] == "take-profit"
        sum_take_profit_hits = (
                                       entry[mask_take_profit_hits]["open"] - entry[mask_take_profit_hits][
                                   "close-price"]).sum() * pip_factor

        mask_stop_loss_hits = entry["close-type"] == "stop-loss"
        sum_stop_loss_hits = (
                                     entry[mask_stop_loss_hits]["open"] - entry[mask_stop_loss_hits][
                                 "close-price"]).sum() * pip_factor

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)
        assert round(sum_take_profit_hits, 0) == 4280
        assert round(sum_stop_loss_hits, 0) == -3405

        entry.to_parquet(f"{OUTPUT_FOLDER}base_case_short.parquet")

    def test_dynamic_stop_loss_case_long(self, prepare_price_data):
        """

        Alternative case: dynamic stop loss long

        Short trade setup passing fix take profit, stop loss levels, and time barrier limit

        """
        df = prepare_price_data

        def calculate_exit(row: any,
                           ohlc: pd.DataFrame,
                           take_profit_width: float,
                           trade_side: TradeSide,
                           pip_decimal_position: int,
                           time_barrier_periods: int):
            barrier_builder = MultiBarrierBuilder(open_price=ohlc.open,
                                                  high_price=ohlc.high,
                                                  low_price=ohlc.low,
                                                  close_price=ohlc.close,
                                                  trade_open_datetime=str(row.name),
                                                  stop_loss_level=row["mva-24"],
                                                  take_profit_pips=take_profit_width,
                                                  trade_side=trade_side,
                                                  pip_decimal_position=pip_decimal_position,
                                                  time_barrier_periods=time_barrier_periods,
                                                  dynamic_exit=ohlc.exit)
            barrier_builder.compute()

            row["close-price"] = barrier_builder.multi_barrier.first_hit.level
            row["close-datetime"] = barrier_builder.multi_barrier.first_hit.hit_datetime
            row["close-type"] = barrier_builder.multi_barrier.first_hit.barrier_type.value

            return row

        take_profit_pips = 10
        strategy_side = TradeSide.BUY
        instrument_pip_position = 4
        time_limit_periods = 10
        pip_factor = 10 ** 4

        entry: pd.DataFrame = df[(df.entry == 1)].copy(deep=True)
        entry = entry.apply(calculate_exit,
                            args=(entry,
                                  take_profit_pips,
                                  strategy_side,
                                  instrument_pip_position,
                                  time_limit_periods),
                            axis=1)

        mask_stop_loss_hits = entry["close-type"] == "stop-loss"
        sum_diff_sl = (entry[mask_stop_loss_hits]["mva-24"] - entry[mask_stop_loss_hits][
            "close-price"]).sum()

        assert {"close-price", "close-datetime", "close-type"}.issubset(entry.columns)
        assert sum_diff_sl == 0

        entry.to_parquet(f"{OUTPUT_FOLDER}alternative_case_dynamic_stop_loss_long.parquet")


