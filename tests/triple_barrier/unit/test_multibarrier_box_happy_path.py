from dateutil import parser

from triple_barrier.orders import Orders
from triple_barrier.orders import MultiBarrierBox
from triple_barrier.orders import BoxBuilder
from triple_barrier.multi_barrier_types import TradeSide


class TestMultiBarrierBox:

    def test_builder_long_levels(self):

        parameters = Orders()
        parameters.open_time = "2023-01-02 02:05:00"
        parameters.trade_side = TradeSide.BUY
        parameters.open_price = 1.07044
        parameters.stop_loss_level = 1.06044
        parameters.take_profit_level = 1.09044
        parameters.time_limit = "2023-01-02 03:05:00"
        parameters.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(parameters)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.06044
        assert multi_barrier_box.take_profit == 1.09044
        assert multi_barrier_box.trade_side == TradeSide.BUY
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_short_levels(self):

        parameters = Orders()
        parameters.open_time = "2023-01-02 02:05:00"
        parameters.trade_side = TradeSide.SELL
        parameters.open_price = 1.07044
        parameters.stop_loss_level = 1.09044
        parameters.take_profit_level = 1.06044
        parameters.time_limit = "2023-01-02 03:05:00"
        parameters.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(parameters)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.09044
        assert multi_barrier_box.take_profit == 1.06044
        assert multi_barrier_box.trade_side == TradeSide.SELL
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_long_width(self):

        parameters = Orders()
        parameters.open_time = "2023-01-02 02:05:00"
        parameters.trade_side = TradeSide.BUY
        parameters.open_price = 1.07044
        parameters.stop_loss_width = 100
        parameters.take_profit_width = 200
        parameters.time_limit = "2023-01-02 03:05:00"
        parameters.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(parameters)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.06044
        assert multi_barrier_box.take_profit == 1.09044
        assert multi_barrier_box.trade_side == TradeSide.BUY
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

    def test_builder_short_width(self):

        parameters = Orders()
        parameters.open_time = "2023-01-02 02:05:00"
        parameters.trade_side = TradeSide.SELL
        parameters.open_price = 1.07044
        parameters.stop_loss_width = 200
        parameters.take_profit_width = 100
        parameters.time_limit = "2023-01-02 03:05:00"
        parameters.pip_decimal_position = 4

        box_builder = BoxBuilder()
        multi_barrier_box = box_builder.build_multi_barrier_box(parameters)

        assert multi_barrier_box.open_datetime == parser.parse("2023-01-02 02:05:00")
        assert multi_barrier_box.stop_loss == 1.09044
        assert multi_barrier_box.take_profit == 1.06044
        assert multi_barrier_box.trade_side == TradeSide.SELL
        assert multi_barrier_box.time_limit == parser.parse("2023-01-02 03:05:00")
        assert multi_barrier_box.pip_decimal_position == 4

