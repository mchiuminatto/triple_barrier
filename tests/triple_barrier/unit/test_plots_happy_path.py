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
