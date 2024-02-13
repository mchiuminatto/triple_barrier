from datetime import datetime
from dateutil import parser
from triple_barrier.triple_barrier import (TradeSide,
                                           BarrierType,
                                           TakeProfit,
                                           StopLoss,
                                           Barrier,
                                           TripleBarrier,
                                           CloseEvent)


class TestTakeProfit:

    def test_static_tp_hit_long_no_level(self, prepare_price_data, prepare_entry_data):
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

        barrier: Barrier = take_profit_barrier.compute()

        assert barrier.level == 1.06759
        assert barrier.hit_datetime == parser.parse("2023-01-02 20:55:00")


class TestStopLoss:
    def test_static_sl_hit_long(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 23:50:00"

        stop_loss_barrier = StopLoss(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       open_datetime=trade_open_datetime,
                                       trade_side=TradeSide.BUY,
                                       pip_decimal_position=4,
                                       stop_loss_width=5
                                       )


        stop_loss: Barrier = stop_loss_barrier.compute()
        assert stop_loss.level == 1.06697
        assert stop_loss.hit_datetime == parser.parse("2023-01-03 00:15:00")
