from datetime import datetime
from dateutil import parser
from triple_barrier.triple_barrier import (TradeSide,
                                           BarrierType,
                                           TakeProfit,
                                           StopLoss,
                                           TimeBarrier,
                                           Barrier,
                                           DynamicBarrier,
                                           MultiBarrierBuilder,
                                           MultiBarrier,
                                           ExitType)


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

        barrier: Barrier = take_profit_barrier.compute()

        assert barrier.level == 1.06759
        assert barrier.hit_datetime == parser.parse("2023-01-02 20:55:00")

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

        barrier: Barrier = take_profit_barrier.compute()

        assert barrier.level == 1.06609
        assert barrier.hit_datetime == parser.parse("2023-01-02 22:05:00")


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
                                     stop_loss_width=5
                                     )

        stop_loss: Barrier = stop_loss_barrier.compute()

        assert stop_loss.level == 1.05535
        assert stop_loss.hit_datetime == parser.parse("2023-01-03 15:25:00")


class TestTimeBarrier:

    def test_time_barrier_hit(self, prepare_price_data):
        trade_open_datetime: str = "2023-01-03 15:00:00"
        df = prepare_price_data
        time_barrier = TimeBarrier(close_price=df.close,
                                   time_barrier_periods=10,
                                   open_datetime=trade_open_datetime)
        time_barrier.compute()

        assert time_barrier.barrier.hit_datetime == parser.parse("2023-01-03 15:00:00")
        assert time_barrier.barrier.level == 1.05577


class TestDynamicBarrier:

    def test_dynamic_barrier_hit(self, prepare_price_data):
        trade_open_datetime: str = "2023-01-03 21:25:00"
        df = prepare_price_data
        dynamic_barrier: DynamicBarrier = DynamicBarrier(
            open_price=df.open,
            exit_signals=df["exit"],
            open_datetime=trade_open_datetime)
        dynamic_barrier.compute()

        assert dynamic_barrier.barrier.level == 1.05681
        assert dynamic_barrier.barrier.hit_datetime == parser.parse("2023-01-04 00:30:00")


class TestTripleBarrier:
    ...

    # case set 1: Full barrier
    def test_full_barrier_setup(self, prepare_price_data):
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=10,
                                              stop_loss_pips=5,
                                              trade_side=TradeSide.SELL,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10)

        barrier_builder.compute()

        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.STOP_LOSS
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")


        ...

    # case 1.1: Long hit take profit
    # case 1.2: Long hit stop loss
    # case 1.3: Long hit time barrier
    # case 1.3: Long hit dynamic barrier

    # case set 2: Time barrier + stop loss or take profit

    # case 2.1 Take profit + Time barrier long, hit take profit
    # case 2.2 Take profit + Time barrier long, hit time barrier
    # case 2.2 Take profit + Time barrier short, hit take profit
    # case 2.3 Take profit + Time barrier short, hit time barrier

    # case 2.4 Stop loss + Time barrier long, hit stop loss
    # case 2.5 Stop loss + Time barrier long, hit time barrier
    # case 2.6 Stop loss + Time barrier short, hit stop loss
    # case 2.7 Stop loss + Time barrier short, hit time barrier

    # case 2.8 Take profit + Dynamic barrier long, hit take profit
    # case 2.9 Take profit + Dynamic barrier long, hit Dynamic barrier
    # case 2.10 Take profit + Dynamic barrier short, hit take profit
    # case 2.11 Take profit + Dynamic barrier short, hit Dynamic barrier

    # case 2.12 Stop loss + Dynamic barrier long, hit stop loss
    # case 2.13 Stop loss + Dynamic barrier long, hit Dynamic barrier
    # case 2.14 Stop loss + Dynamic barrier short, hit stop loss
    # case 2.15 Stop loss + Dynamic barrier short, hit Dynamic barrier

    # case set 3: Only time barrier

    # case 3.1 time barrier long
    # case 3.2 time barrier short

    # case set 4: Only dynamic barrier
    # case 4.1 dynamic barrier long
    # case 4.2 dynamic barrier short
