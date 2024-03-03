from dateutil import parser
import pandas as pd

from triple_barrier import constants
from triple_barrier.plots import PlotTripleBarrier
from triple_barrier.triple_barrier import TradeSide

class TestPlots:

    def test_build_ohlc(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)

        ohlc = plotter.build_ohlc(df[constants.OPEN],
                                  df[constants.HIGH],
                                  df[constants.LOW],
                                  df[constants.CLOSE])

        assert (ohlc[constants.OPEN] - df[constants.OPEN]).sum() == 0
        assert (ohlc[constants.HIGH] - df[constants.HIGH]).sum() == 0
        assert (ohlc[constants.LOW] - df[constants.LOW]).sum() == 0
        assert (ohlc[constants.CLOSE] - df[constants.CLOSE]).sum() == 0

    def test_calculate_take_profit_level_long(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)

        take_profit_level = plotter.calculate_take_profit_level(1.1300, 20, TradeSide.BUY)
        assert take_profit_level == 1.1320

    def test_calculate_take_profit_level_short(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)

        take_profit_level = plotter.calculate_take_profit_level(1.1300, 20, TradeSide.SELL)
        assert take_profit_level == 1.1280

    def test_calculate_stop_loss_level_long(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)

        take_profit_level = plotter.calculate_stop_loss_level(1.1300, 20, TradeSide.BUY)
        assert take_profit_level == 1.1280

    def test_calculate_stop_loss_level_short(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)

        take_profit_level = plotter.calculate_stop_loss_level(1.1300, 20, TradeSide.SELL)
        assert take_profit_level == 1.1320

    def test_calculate_time_barrier_datetime(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(df[constants.OPEN],
                                    df[constants.HIGH],
                                    df[constants.LOW],
                                    df[constants.CLOSE],
                                    pip_decimal_position=4)
        time_barrier_datetime = plotter.calculate_time_limit_datetime("2023-01-02 23:50:00",
                                                                      10)
        assert time_barrier_datetime == parser.parse("2023-01-03 00:40:00")
