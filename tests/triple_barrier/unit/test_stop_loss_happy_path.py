from dateutil import parser
from triple_barrier.trade_labeling import StopLoss
from triple_barrier.types import TradeSide


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
                                     stop_loss=1.06697
                                     )

        stop_loss_barrier.compute()
        assert stop_loss_barrier.barrier.level == 1.06697
        assert stop_loss_barrier.barrier.hit_datetime == parser.parse("2023-01-03 00:15:00")

    def test_static_sl_hit_short(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-03 14:45:00"

        stop_loss_barrier = StopLoss(open_price=df.open,
                                     high_price=df.high,
                                     low_price=df.low,
                                     close_price=df.close,
                                     open_datetime=trade_open_datetime,
                                     trade_side=TradeSide.SELL,
                                     pip_decimal_position=4,
                                     stop_loss=1.05535
                                     )

        stop_loss_barrier.compute()

        assert stop_loss_barrier.barrier.level == 1.05535
        assert stop_loss_barrier.barrier.hit_datetime == parser.parse("2023-01-03 15:25:00")
