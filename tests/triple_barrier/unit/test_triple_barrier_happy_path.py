
import pandas as pd
from dateutil import parser
from triple_barrier.triple_barrier import (TradeSide,
                                           BarrierType,
                                           TimeBarrier,
                                           DynamicBarrier,
                                           MultiBarrierBuilder
                                           )


class TestTripleBarrier:

    def test_full_barrier_hit_take_profit_long(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits take profit, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=5,
                                              stop_loss_pips=5,
                                              trade_side=TradeSide.BUY,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df.exit)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TAKE_PROFIT
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_full_barrier_stop_loss_short(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits stop loss, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=5,
                                              stop_loss_pips=5,
                                              trade_side=TradeSide.SELL,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.STOP_LOSS
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_full_barrier_time_barrier_short(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits time barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=20,
                                              stop_loss_pips=20,
                                              trade_side=TradeSide.SELL,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TIME_BARRIER
        assert barrier_builder.multi_barrier.first_hit.level == 1.06710
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 21:35:00")

    def test_full_barrier_time_barrier_hit_long(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits time barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=20,
                                              stop_loss_pips=20,
                                              trade_side=TradeSide.BUY,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TIME_BARRIER
        assert barrier_builder.multi_barrier.first_hit.level == 1.06710
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 21:35:00")

    def test_full_barrier_dynamic_hit_long(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits dynamic barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=20,
                                              stop_loss_pips=20,
                                              trade_side=TradeSide.BUY,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df["exit-signal"])

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.DYNAMIC
        assert barrier_builder.multi_barrier.first_hit.level == 1.06766
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 21:05:00")

    def test_full_barrier_dynamic_hit_short(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits dynamic barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=20,
                                              stop_loss_pips=20,
                                              trade_side=TradeSide.SELL,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df["exit-signal"])

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.DYNAMIC
        assert barrier_builder.multi_barrier.first_hit.level == 1.06766
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 21:05:00")

    def test_time_barrier_take_profit_hit_long(self, prepare_price_data):
        """
            Test no stop loss barrier for a long trade that hits take profit barrier, with take profit
            distance in pips.
        """

        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=5,
                                              trade_side=TradeSide.BUY,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df.exit)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TAKE_PROFIT
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_time_barrier_stop_loss_hit_short(self, prepare_price_data):
        """
            Test no take profit barrier for a short trade that hits stop loss barrier, with take profit
            distance in pips.
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              stop_loss_pips=5,
                                              trade_side=TradeSide.SELL,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df.exit)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.STOP_LOSS
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_sl_tp_levels_long(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits take profit, with stop loss and take profit
            price levels
        """
        df = prepare_price_data
        barrier_builder = MultiBarrierBuilder(open_price=df.open,
                                              high_price=df.high,
                                              low_price=df.low,
                                              close_price=df.close,
                                              trade_open_datetime="2023-01-02 20:45:00",
                                              take_profit_pips=1.06759,
                                              stop_loss_pips=5,
                                              trade_side=TradeSide.BUY,
                                              pip_decimal_position=4,
                                              time_barrier_periods=10,
                                              dynamic_exit=df.exit)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TAKE_PROFIT
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

# TODO: Add more tests

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
