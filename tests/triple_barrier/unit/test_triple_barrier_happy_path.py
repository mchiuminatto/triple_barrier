import pandas as pd
from dateutil import parser
from triple_barrier.triple_barrier import (TradeSide,
                                           BarrierType,
                                           MultiBarrier,
                                           )
from triple_barrier.multi_barrier_box import MultiBarrierParameters


class TestTripleBarrier:

    def test_full_barrier_hit_take_profit_long_width(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits take profit, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data

        stop_loss: float = 5
        take_profit: float = 5
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.BUY

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = df[box_setup.open_time:].index[10]
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       dynamic_exit=df.exit,
                                       box_setup=box_setup)

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TAKE_PROFIT
        assert barrier_builder.multi_barrier.first_hit.level == 1.06759
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

    def test_full_barrier_stop_loss_short_width(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits stop loss, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data

        stop_loss: float = 5
        take_profit: float = 5
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.SELL
        time_barrier_periods: int = 10

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = df[box_setup.open_time:].index[time_barrier_periods]
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup
                                       )

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

        stop_loss: float = 20
        take_profit: float = 25
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.SELL

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 23:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup
                                       )
        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TIME_BARRIER
        assert barrier_builder.multi_barrier.first_hit.level == 1.0663
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 23:00:00")

    def test_full_barrier_time_barrier_hit_long(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits time barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data

        stop_loss: float = 20
        take_profit: float = 20
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.BUY

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup
                                       )

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

        stop_loss: float = 20
        take_profit: float = 20
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.BUY

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup,
                                       dynamic_exit=df["exit-signal"]
                                       )

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
        trade_open_datetime: str = "2023-01-02 20:45:00"
        trade_side: TradeSide = TradeSide.SELL

        stop_loss: float = 20
        take_profit: float = 20
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.SELL

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup,
                                       dynamic_exit=df["exit-signal"]
                                       )

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.DYNAMIC
        assert barrier_builder.multi_barrier.first_hit.level == 1.06766
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 21:05:00")

    def test_sl_tp_levels_long_tp_level(self, prepare_price_data):
        """
            Test full barrier for a long trade that hits take profit, with stop loss distance in pips and take profit
            as price level.
        """
        df = prepare_price_data

        stop_loss: float = 1.0641
        take_profit: float = 1.0671
        open_datetime: str = "2023-01-02 22:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.BUY

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_level = take_profit
        box_setup.stop_loss_level = stop_loss
        box_setup.time_limit = "2023-01-03 01:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup,
                                       dynamic_exit=df["exit-signal"]
                                       )

        barrier_builder.compute()
        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.TAKE_PROFIT
        assert barrier_builder.multi_barrier.first_hit.level == 1.0671
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-02 23:40:00")

    def test_sl_tp_levels_long_short_sl_level(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits stop loss, with take profit
            distance in pips and stop loss as price level.
        """
        df = prepare_price_data

        stop_loss: float = 1.05549
        take_profit: float = 1.0525
        open_datetime: str = "2023-01-03 20:30:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.SELL

        box_setup = MultiBarrierParameters()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_level = take_profit
        box_setup.stop_loss_level = stop_loss
        box_setup.time_limit = "2023-01-03 23:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position
        barrier_builder = MultiBarrier(open_price=df.open,
                                       high_price=df.high,
                                       low_price=df.low,
                                       close_price=df.close,
                                       box_setup=box_setup
                                       )
        barrier_builder.compute()

        assert barrier_builder.multi_barrier.first_hit.barrier_type == BarrierType.STOP_LOSS
        assert barrier_builder.multi_barrier.first_hit.level == 1.05549
        assert barrier_builder.multi_barrier.first_hit.hit_datetime == parser.parse("2023-01-03  21:05:00")



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
