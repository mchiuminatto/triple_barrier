from dateutil import parser
from triple_barrier.trade_labeling import (TradeSide,
                                           OrderType,
                                           Labeler,
                                           )
from triple_barrier.orders import Orders


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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = df[box_setup.open_time:].index[10]
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  dynamic_exit=df.exit,
                                  box_setup=box_setup)

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.TAKE_PROFIT
        assert barrier_builder.orders_hit.first_hit.level == 1.06759
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = df[box_setup.open_time:].index[time_barrier_periods]
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup
                                  )

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.STOP_LOSS
        assert barrier_builder.orders_hit.first_hit.level == 1.06759
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 20:55:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 23:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup
                                  )
        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.TIME_EXPIRATION
        assert barrier_builder.orders_hit.first_hit.level == df["open"]["2023-01-02 23:00:00":].iloc[1]
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 23:00:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup
                                  )

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.TIME_EXPIRATION
        assert barrier_builder.orders_hit.first_hit.level == df["open"]["2023-01-02 21:35:00":].iloc[1]
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 21:35:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup,
                                  dynamic_exit=df["exit-signal"]
                                  )

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.DYNAMIC
        assert barrier_builder.orders_hit.first_hit.level == 1.06766
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 21:05:00")

    def test_full_barrier_dynamic_hit_short(self, prepare_price_data):
        """
            Test full barrier for a short trade that hits dynamic barrier, with stop loss and take profit
            distance in pips.
        """
        df = prepare_price_data
        # trade_open_datetime: str = "2023-01-02 20:45:00"
        # trade_side: TradeSide = TradeSide.SELL

        stop_loss: float = 20
        take_profit: float = 20
        open_datetime: str = "2023-01-02 20:45:00"
        pip_decimal_position = 4
        trade_side: TradeSide = TradeSide.SELL

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_width = take_profit
        box_setup.stop_loss_width = stop_loss
        box_setup.time_limit = "2023-01-02 21:35:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup,
                                  dynamic_exit=df["exit-signal"]
                                  )

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.DYNAMIC
        assert barrier_builder.orders_hit.first_hit.level == 1.06766
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 21:05:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_level = take_profit
        box_setup.stop_loss_level = stop_loss
        box_setup.time_limit = "2023-01-03 01:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position

        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup,
                                  dynamic_exit=df["exit-signal"]
                                  )

        barrier_builder.compute()
        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.TAKE_PROFIT
        assert barrier_builder.orders_hit.first_hit.level == 1.0671
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-02 23:40:00")

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

        box_setup = Orders()
        box_setup.open_time = open_datetime
        box_setup.open_price = df.loc[box_setup.open_time]["open"]
        box_setup.take_profit_level = take_profit
        box_setup.stop_loss_level = stop_loss
        box_setup.time_limit = "2023-01-03 23:00:00"
        box_setup.trade_side = trade_side
        box_setup.pip_decimal_position = pip_decimal_position
        barrier_builder = Labeler(open_price=df.open,
                                  high_price=df.high,
                                  low_price=df.low,
                                  close_price=df.close,
                                  box_setup=box_setup
                                  )
        barrier_builder.compute()

        assert barrier_builder.orders_hit.first_hit.order_type == OrderType.STOP_LOSS
        assert barrier_builder.orders_hit.first_hit.level == 1.05549
        assert barrier_builder.orders_hit.first_hit.hit_datetime == parser.parse("2023-01-03  21:05:00")
