
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
                 oscillator_features: list | None = None,
                 save_plot: bool = True,
                 plot_folder: str = "./",
                 periods_before: int = 5,
                 periods_after: int = 5
                 ):
        """ Plotting class for triple barrier method trades.
        
        :param open_price: Series of open prices
        :param high_price: Series of high prices
        :param low_price: Series of low prices
        :param close_price: Series of close prices
        :param pip_decimal_position: Decimal position of the pip (e.g. 4 for EUR/USD)
        :param overlay_features: List of features to overlay on the plot (e.g. moving averages)
        :param oscillator_features: List of oscillator features to plot in the second panel (e.g. AWO)
        :param save_plot: Boolean to save the plot (default True)
        :param plot_folder: Folder to save the plot if save_plot is True (default "./")
        :param periods_before: Number of periods to extend the plot before the entry period (default 5)
        :param periods_after: Number of periods to extend the plot after the time barrier (default 5)
    
        """        

        self._periods_after: int = periods_after
        self._periods_before: int = periods_before

        if overlay_features is None:
            self.overlay_features = []
        else:
            self.overlay_features: list = overlay_features
            
        if oscillator_features is None:
            self.oscillator_features = []
        else:
            self.oscillator_features: list = oscillator_features

        self.ohlc = self.build_ohlc(open_price,
                                    high_price,
                                    low_price,
                                    close_price)
        self.pip_factor = 10 ** (-pip_decimal_position)
        self.barrier_lines: list | None = None
        self.save_plot: bool = save_plot
        self.plot_folder = plot_folder

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
            dynamic_exit_price=None,
            closing_event=multi_barrier.orders_hit.first_hit
        )

    def _plot(self,
              entry_period: datetime,
              take_profit_level: float,
              stop_loss_level: float,
              time_barrier_datetime: datetime,
              dynamic_exit_price: float | None = None,
              closing_event: OrderHit | None = None
              ):

        # date_from: datetime = entry_period
        # date_to: datetime = closing_event.hit_datetime if closing_event is not None else self.ohlc.index[-1]
        
        date_from, date_to = self._calculate_plotting_range_extension(
            entry_period,
            pd.to_datetime(time_barrier_datetime)
        )
    
    
        if len(self.ohlc[date_from: date_to]) == 0:
            raise ValueError("No data to process")

        barrier: dict = {
            constants.OPEN_TIME: entry_period,
            constants.OPEN_PRICE: self.ohlc.loc[entry_period]["open"],
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
                                          panel=0
                                          )
                         )
            
        for feature in self.oscillator_features:
            plots.append(mpf.make_addplot(feature[date_from: date_to],
                                          type="line",
                                          label=feature.name,
                                          width=0.5,
                                          panel=1
                                          )
                         )

        if closing_event is not None:
            plots.append(
                self._add_closing_event_hit(date_from, date_to, closing_event)
            )

        
        barrier_lines = self._build_barrier_lines(date_from, date_to, barrier)
            
        print("Barrier lines:", barrier_lines)

        fig, ax = mpf.plot(self.ohlc[date_from:date_to],
                           type="candle", figsize=(15, 4),
                           style="ibd",
                           alines=barrier_lines,
                           addplot=plots,
                           returnfig=True)

        self._add_text(barrier, ax, date_from, date_to)
        if self.save_plot:
            plt.savefig(f"{self.plot_folder}triple_barrier_{entry_period.strftime('%Y-%m-%d %H_%M_%S')}.png")
            plt.close()
        else:
            plt.show()
    
    
    def _calculate_plotting_range_extension(self, date_from: datetime, date_to: datetime) -> tuple[datetime, datetime]:
        """
        Calculate the plotting range for the given date range.
        Extends the range by a specified number of periods before and after.
        """
        start_index = self.ohlc.index.get_loc(date_from)
        end_index = self.ohlc.index.get_loc(date_to)

        start_index = max(0, start_index - self._periods_before)
        end_index = min(len(self.ohlc) - 1, end_index + self._periods_after)

        extended_date_from = self.ohlc.index[start_index]
        extended_date_to = self.ohlc.index[end_index]

        return extended_date_from, extended_date_to
        

    def _add_closing_event_hit(self,
                               date_from: datetime,
                               date_to: datetime,
                               closing_event: OrderHit) -> dict:

        # TODO: move this logic to a function that returns the make_addplot object
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
        open_time: datetime = barrier[constants.OPEN_TIME]
        
        top_line_level: float = max(take_profit, stop_loss, -float("inf") if dynamic_close is None else dynamic_close)
        bottom_line_level: float = min(take_profit, stop_loss, float("inf") if dynamic_close is None else dynamic_close)

        take_profit_line: list = [(open_time, take_profit), (time_limit, take_profit)]
        stop_loss_line: list = [(open_time, stop_loss), (time_limit, stop_loss)]
        open_vertical_line: list = [(open_time, bottom_line_level), (open_time, top_line_level)]
        time_barrier_vertical_line: list = [(time_limit, bottom_line_level), (time_limit, top_line_level)]
        open_line: list = [(open_time, open_price), (time_limit, open_price)]

        barrier_lines = [
            take_profit_line,
            stop_loss_line,
            time_barrier_vertical_line,
            open_vertical_line,
            open_line
        ]
        if dynamic_close is not None:
            barrier_lines.append([(open_time, dynamic_close), (time_limit, dynamic_close)])

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
