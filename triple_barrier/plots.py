from datetime import datetime
import pandas as pd

import matplotlib.pyplot as plt
import mplfinance as mpl
from triple_barrier.triple_barrier import TradeSide, TakeProfit, StopLoss


class PlotTripleBarrier:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 pip_decimal_position: int,
                 ):

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

    def plot_triple_barrier(self,
                            entry_period: str,
                            take_profit_width: float,
                            stop_loss_width: float,
                            time_barrier_periods: int,
                            trade_side: TradeSide,
                            dynamic_barrier: object = None,
                            periods_to_plot: int = 50
                            ):

        date_from = pd.to_datetime(entry_period)
        date_to = self.ohlc[entry_period:].index[periods_to_plot]

        if len(self.ohlc[date_from: date_to]) == 0:
            raise ValueError("No data to process")

        print("Plotting barrier for", len(self.ohlc[date_from: date_to]))

        open_price = self.ohlc.loc[date_from]["open"]
        stop_loss = self.calculate_stop_loss_level(open_price, stop_loss_width, trade_side)
        take_profit = self.calculate_take_profit_level(open_price, take_profit_width, trade_side)
        time_limit = self.calculate_time_limit_datetime(date_from, time_barrier_periods)

        print("Open price", open_price)
        print("Take profit", take_profit)
        print("Stop loss", stop_loss)
        print("Time barrier", time_limit)

        plots = [
            # mpl.make_addplot(self.ohlc[date_from: date_to]["mva-12"], label="mva-12"),
            # mpl.make_addplot(self.ohlc[date_from: date_to]["mva-24"], label="mva-24"),
            # mpl.make_addplot(self.ohlc[date_from: date_to]["entry-mark"], type="scatter", marker="^", color="red")
        ]

        barrier_points = [
            (date_from, take_profit), (time_limit, take_profit),
            (time_limit, stop_loss), (date_from, stop_loss),
            (date_from, stop_loss), (date_from, take_profit),
        ]

        barrier_lines = dict(alines=barrier_points,
                             linewidths=[0.5],
                             colors=["r", "g"],
                             linestyle=["-.", "-."],
                             alpha=0.5)

        if "stop-loss-hit-mark" in self.ohlc.columns:
            count_not_null = self.ohlc[date_from: date_to]["stop-loss-hit-mark"].count()
            if count_not_null != 0:
                plots.append(
                    mpl.make_addplot(self.ohlc[date_from: date_to]["stop-loss-hit-mark"], type="scatter", marker="*",
                                     color="blue"))
        if "take-profit-hit-mark" in self.ohlc.columns:
            count_not_null = self.ohlc[date_from: date_to]["take-profit-hit-mark"].count()
            if count_not_null != 0:
                print("fall here")
                plots.append(
                    mpl.make_addplot(self.ohlc[date_from: date_to]["take-profit-hit-mark"], type="scatter",
                                     marker="*",
                                     color="yellow"))

        if "condition-hit-mark" in self.ohlc.columns:
            count_not_null = self.ohlc[date_from: date_to]["condition-hit-mark"].count()
            if count_not_null != 0:
                plots.append(
                    mpl.make_addplot(self.ohlc[date_from: date_to]["condition-hit-mark"], type="scatter", marker="8",
                                     color="yellow"))

        mpl.plot(self.ohlc[date_from:date_to],
                 type="candle", figsize=(15, 4),
                 style="ibd",
                 alines=barrier_lines,
                 addplot=plots)

        plt.show()

    def calculate_take_profit_level(self, open_price: float,
                                    take_profit_width: float,
                                    trade_side: TradeSide):

        return open_price + trade_side.value * take_profit_width * self.pip_factor

    def calculate_stop_loss_level(self,
                                  open_price: float,
                                  take_profit_width: float,
                                  trade_side: TradeSide):

        return open_price - trade_side.value * take_profit_width * self.pip_factor

    def calculate_time_limit_datetime(self,
                                      date_from: datetime,
                                      time_barrier_periods: int
                                      ) -> datetime:

        self.ohlc["temp-date-time"] = self.ohlc.index
        self.ohlc["time-limit"] = self.ohlc["temp-date-time"].shift(-time_barrier_periods)
        time_limit = self.ohlc.loc[date_from]["time-limit"]
        self.ohlc.drop(columns=["temp-date-time", "time-limit"], inplace=True)
        return time_limit
