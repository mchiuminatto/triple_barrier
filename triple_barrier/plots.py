# TODO: Move all this logic to a single file

from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import mplfinance as mpf

from triple_barrier.trade_labeling import OrderHit
from triple_barrier.trade_labeling import Labeler

from triple_barrier import constants


class PlotTripleBarrier:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 pip_decimal_position: int,
                 overlay_features: list | None = None,
                 periods_to_plot: int = 50
                 ):

        self._periods_to_plot: int = periods_to_plot

        if overlay_features is None:
            self.overlay_features = []
        else:
            self.overlay_features: list = overlay_features

        self.ohlc = self.build_ohlc(open_price,
                                    high_price,
                                    low_price,
                                    close_price)
        self.pip_factor = 10 ** (-pip_decimal_position)
        self.barrier_lines: list | None = None

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

    def plot_multi_barrier(self,
                           multi_barrier: Labeler):
        self._plot(
            entry_period=multi_barrier.multi_barrier_box.open_datetime,
            take_profit_level=multi_barrier.multi_barrier_box.take_profit,
            stop_loss_level=multi_barrier.multi_barrier_box.stop_loss,
            time_barrier_datetime=multi_barrier.multi_barrier_box.time_limit,
            periods_to_plot=self._periods_to_plot,
            dynamic_exit_price=None,
            closing_event=multi_barrier.orders_hit.first_hit
        )

    def _plot(self,
              entry_period: datetime,
              take_profit_level: float,
              stop_loss_level: float,
              time_barrier_datetime: datetime,
              periods_to_plot: int = 50,
              dynamic_exit_price: float | None = None,
              closing_event: OrderHit | None = None
              ):

        date_from: datetime = entry_period
        date_to: datetime = self.ohlc[entry_period:].index[periods_to_plot - 1]

        if len(self.ohlc[date_from: date_to]) == 0:
            raise ValueError("No data to process")

        barrier: dict = {
            constants.OPEN_PRICE: self.ohlc.loc[date_from]["open"],
            constants.STOP_LOSS: stop_loss_level,
            constants.TAKE_PROFIT: take_profit_level,
            constants.DYNAMIC_CLOSE: dynamic_exit_price,
            constants.TIME_LIMIT: pd.to_datetime(time_barrier_datetime),
        }

        print("Plotting barrier for", len(self.ohlc[date_from: date_to]))
        plots: list = []

        for feature in self.overlay_features:
            plots.append(mpf.make_addplot(feature[date_from: date_to],
                                          type="line",
                                          marker="8",
                                          label=feature.name,
                                          width=0.5,
                                          )
                         )

        if closing_event is not None:
            plots.append(
                self._add_closing_event_hit(date_from, date_to, closing_event)
            )

        barrier_lines = self._build_barrier_lines(date_from, date_to, barrier)

        fig, ax = mpf.plot(self.ohlc[date_from:date_to],
                           type="candle", figsize=(15, 4),
                           style="ibd",
                           alines=barrier_lines,
                           addplot=plots,
                           returnfig=True)

        self._add_text(barrier, ax, date_from, date_to)

        plt.show()

        # TODO: store binary image in a file to compare with a stored one for testing purposes

    def _add_closing_event_hit(self,
                               date_from: datetime,
                               date_to: datetime,
                               closing_event: OrderHit) -> dict:

        # move this logic to a function that returns the make_addplot object
        self.ohlc["temp-dynamic"] = np.nan
        high = (self.ohlc.loc[closing_event.hit_datetime, "high"]
                + (self.ohlc.loc[closing_event.hit_datetime, "high"]
                   - self.ohlc.loc[closing_event.hit_datetime, "low"]) * 1.05)
        self.ohlc.loc[closing_event.hit_datetime, "temp-dynamic"] = high

        return mpf.make_addplot(self.ohlc[date_from: date_to]["temp-dynamic"],
                                type="scatter",
                                marker="v",
                                markersize=75,
                                color="red"
                                )

    @staticmethod
    def _build_barrier_lines(date_from: datetime,
                             date_to: datetime,
                             barrier: dict) -> dict:

        take_profit: float = barrier[constants.TAKE_PROFIT]
        stop_loss: float = barrier[constants.STOP_LOSS]
        open_price: float = barrier[constants.OPEN_PRICE]
        time_limit: datetime = barrier[constants.TIME_LIMIT]
        dynamic_close: float = barrier[constants.DYNAMIC_CLOSE]

        top_line_level: float = max(take_profit, stop_loss, -float("inf") if dynamic_close is None else dynamic_close)
        bottom_line_level: float = min(take_profit, stop_loss, float("inf") if dynamic_close is None else dynamic_close)

        take_profit_line: list = [(date_from, take_profit), (time_limit, take_profit)]
        stop_loss_line: list = [(date_from, stop_loss), (time_limit, stop_loss)]
        open_vertical_line: list = [(date_from, bottom_line_level), (date_from, top_line_level)]
        time_barrier_vertical_line: list = [(time_limit, bottom_line_level), (time_limit, top_line_level)]
        open_line: list = [(date_from, open_price), (time_limit, open_price)]

        barrier_lines = [
            take_profit_line,
            stop_loss_line,
            time_barrier_vertical_line,
            open_vertical_line,
            open_line
        ]
        if dynamic_close is not None:
            barrier_lines.append([(date_from, dynamic_close), (time_limit, dynamic_close)])

        colors = ["g", "r", "b", "b", "black", "grey"]

        barrier_lines = dict(alines=barrier_lines,
                             linewidths=[1.5],
                             colors=colors,
                             linestyle=["--", "--"],
                             alpha=0.5)

        return barrier_lines

    def _add_text(self,
                  barrier: dict,
                  axis: list,
                  date_from,
                  date_to):

        font = {"family": "serif",
                "color": "black",
                "weight": "normal",
                "size": 10,
                "backgroundcolor": "white"
                }

        time_limit_index = self.ohlc[date_from:date_to].index.get_loc(barrier[constants.TIME_LIMIT]) + 1
        axis[0].text(time_limit_index,
                     barrier[constants.OPEN_PRICE],
                     "open",
                     fontdict=font)

        font["color"] = "green"
        axis[0].text(time_limit_index,
                     barrier[constants.TAKE_PROFIT],
                     "tp",
                     fontdict=font)

        font["color"] = "red"
        axis[0].text(time_limit_index,
                     barrier[constants.STOP_LOSS],
                     "sl",
                     fontdict=font)

        if barrier[constants.DYNAMIC_CLOSE] is not None:
            font["color"] = "grey"
            axis[0].text(time_limit_index,
                         barrier[constants.DYNAMIC_CLOSE],
                         "dyb",
                         fontdict=font)
