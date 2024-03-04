# TODO: Move all this logic to a single file

import pandas as pd

import matplotlib.pyplot as plt
import mplfinance as mpf


class PlotTripleBarrier:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 pip_decimal_position: int,
                 overlay_features: list = None
                 ):

        if overlay_features is None:
            self.overlay_features = []
        else:
            self.overlay_features: list = overlay_features

        self.ohlc = self.build_ohlc(open_price,
                                    high_price,
                                    low_price,
                                    close_price)
        self.pip_factor = 10 ** (-pip_decimal_position)

    @staticmethod
    def build_ohlc(open_price: pd.Series,
                   high_price: pd.Series,
                   low_price: pd.Series,
                   close_price: pd.Series) -> pd.DataFrame:

        ohlc = pd.DataFrame({"open": open_price,
                             "high": high_price,
                             "low": low_price,
                             "close": close_price},
                            columns=["open", "high", "low", "close"])
        return ohlc

    def plot(self,
             entry_period: str,
             take_profit_level: float,
             stop_loss_level: float,
             time_barrier_datetime: str,
             periods_to_plot: int = 50,
             dynamic_exit_datetime: str = None
             ):

        date_from = pd.to_datetime(entry_period)
        date_to = self.ohlc[entry_period:].index[periods_to_plot]

        if len(self.ohlc[date_from: date_to]) == 0:
            raise ValueError("No data to process")

        print("Plotting barrier for", len(self.ohlc[date_from: date_to]))

        open_price: float = self.ohlc.loc[date_from]["open"]
        stop_loss: float = stop_loss_level
        take_profit: float = take_profit_level
        time_limit = pd.to_datetime(time_barrier_datetime)

        plots: list = []

        for feature in self.overlay_features:
            plots.append(mpf.make_addplot(feature[date_from:date_to], type="line", marker="8", label=feature.name))

        barrier_points = [
            [(date_from, take_profit), (time_limit, take_profit)],
            [(date_from, stop_loss), (time_limit, stop_loss)],
            [(date_from, stop_loss), (date_from, take_profit)],
            [(time_limit, stop_loss), (time_limit, take_profit)],
            [(date_from, open_price), (time_limit, open_price)]
        ]

        colors: list = []
        if take_profit > stop_loss:
            colors = ["g", "r", "b", "b", "black"]
        else:
            colors = ["r", "g", "b", "b", "black"]

        barrier_lines = dict(alines=barrier_points,
                             linewidths=[0.5],
                             colors=colors,
                             linestyle=["-.", "-."],
                             alpha=0.5)

        mpf.plot(self.ohlc[date_from:date_to],
                 type="candle", figsize=(15, 4),
                 style="ibd",
                 alines=barrier_lines,
                 addplot=plots)

        plt.show()
