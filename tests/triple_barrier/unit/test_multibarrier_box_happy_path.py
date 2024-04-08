from dateutil import parser

from triple_barrier.orders import Orders
from triple_barrier.orders import BoxBuilder
from triple_barrier.types import TradeSide


class TestMultiBarrierBox:

    def test_builder_long_levels(self):
        orders = Orders()
        orders.open_time = "2023-01-02 02:05:00"
        orders.trade_side = TradeSide.BUY
        orders.open_price = 1.07044
        orders.stop_loss_level = 1.06044
        orders.take_profit_level = 1.09044
        orders.time_limit = "2023-01-02 03:05:00"
        orders.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(orders)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.06044
        assert multi_barrier_box.take_profit == 1.09044
        assert multi_barrier_box.trade_side == TradeSide.BUY
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_short_levels(self):
        orders = Orders()
        orders.open_time = "2023-01-02 02:05:00"
        orders.trade_side = TradeSide.SELL
        orders.open_price = 1.07044
        orders.stop_loss_level = 1.09044
        orders.take_profit_level = 1.06044
        orders.time_limit = "2023-01-02 03:05:00"
        orders.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(orders)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.09044
        assert multi_barrier_box.take_profit == 1.06044
        assert multi_barrier_box.trade_side == TradeSide.SELL
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_long_width(self):
        orders = Orders()
        orders.open_time = "2023-01-02 02:05:00"
        orders.trade_side = TradeSide.BUY
        orders.open_price = 1.07044
        orders.stop_loss_width = 100
        orders.take_profit_width = 200
        orders.time_limit = "2023-01-02 03:05:00"
        orders.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(orders)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.06044
        assert multi_barrier_box.take_profit == 1.09044
        assert multi_barrier_box.trade_side == TradeSide.BUY
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_short_width(self):
        orders = Orders()
        orders.open_time = "2023-01-02 02:05:00"
        orders.trade_side = TradeSide.SELL
        orders.open_price = 1.07044
        orders.stop_loss_width = 200
        orders.take_profit_width = 100
        orders.time_limit = "2023-01-02 03:05:00"
        orders.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(orders)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.09044
        assert multi_barrier_box.take_profit == 1.06044
        assert multi_barrier_box.trade_side == TradeSide.SELL
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4
