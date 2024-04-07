from datetime import datetime
from dateutil import parser

import numpy as np
import pandas as pd

from triple_barrier.trade_labeler import TakeProfit
from triple_barrier.multi_barrier_types import TradeSide
from triple_barrier import constants


class TestTakeProfit:

    def test_static_tp_hit_long(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: datetime = pd.to_datetime("2023-01-02 20:45:00")

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.BUY,
                                         pip_decimal_position=4,
                                         take_profit=1.06759
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == 1.06759
        assert take_profit_barrier.barrier.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_static_tp_hit_short(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: datetime = pd.to_datetime("2023-01-02 22:00:00")

        take_profit_barrier = TakeProfit(open_price=df.open,
                                         high_price=df.high,
                                         low_price=df.low,
                                         close_price=df.close,
                                         open_datetime=trade_open_datetime,
                                         trade_side=TradeSide.SELL,
                                         pip_decimal_position=4,
                                         take_profit=1.06609
                                         )

        take_profit_barrier.compute()

        assert take_profit_barrier.barrier.level == 1.06609
        assert take_profit_barrier.barrier.hit_datetime == parser.parse("2023-01-02 22:05:00")






