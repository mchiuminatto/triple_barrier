import numpy as np
import pandas as pd
from dateutil import parser
from triple_barrier.triple_barrier import (TradeSide,
                                           TakeProfit,)
from triple_barrier import constants


class TestTakeProfit:

    def test_static_tp_hit_long(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 20:45:00"

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.BUY,
                                         pip_decimal_position=4,
                                         take_profit_width=5
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == 1.06759
        assert take_profit_barrier.barrier.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_static_tp_hit_short(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 22:00:00"

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.SELL,
                                         pip_decimal_position=4,
                                         take_profit_width=10
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == 1.06609
        assert take_profit_barrier.barrier.hit_datetime == parser.parse("2023-01-02 22:05:00")

    def test_take_profit_level_hit_short(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 22:00:00"

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.SELL,
                                         pip_decimal_position=4,
                                         take_profit_level=1.06609
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == 1.06609
        assert take_profit_barrier.barrier.hit_datetime == parser.parse("2023-01-02 22:05:00")

    def test_take_profit_no_level_no_width_short(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 22:00:00"

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.SELL,
                                         pip_decimal_position=4
                                         )

        take_profit_barrier.compute()
        assert take_profit_barrier.barrier.level == -np.inf
        assert take_profit_barrier.barrier.hit_datetime == constants.INFINITE_DATE

    def test_take_profit_no_level_no_width_long(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 22:00:00"

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.BUY,
                                         pip_decimal_position=4
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == np.inf
        assert take_profit_barrier.barrier.hit_datetime == constants.INFINITE_DATE



