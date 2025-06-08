"""
This class implements an abstraction for applying a trading setup on
a Pandas dataset

"""

from dataclasses import dataclass
import pandas as pd

from .trade_labeling import TradeSide
from .orders import Orders
from .trade_labeling import Labeler
import triple_barrier.constants as const
from triple_barrier.plots import PlotTripleBarrier

from datetime import datetime


@dataclass
class TradingParameters:
    open_price: pd.DataFrame
    high_price: pd.DataFrame
    low_price: pd.DataFrame
    close_price: pd.DataFrame
    entry_mark: pd.DataFrame
    stop_loss_width: float
    take_profit_width: float
    trade_side: TradeSide
    pip_decimal_position: int
    time_barrier_periods: int
    dynamic_exit: pd.Series | None = None


class DataSetLabeler:
    """
    Class that makes abstraction of executing an apply function
    on a Pandas dataset, avoiding the user some validations. Facade pattern
    """
    
    ENTRY = "entry"
    EXIT = "exit"
    
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"

    def __init__(self, trading_setup: TradingParameters):
        
        self.trades: pd.DataFrame | None = None
        self._trading_setup = trading_setup
        ohlc_series: dict = {
            self.OPEN: trading_setup.open_price,
            self.HIGH: trading_setup.high_price,
            self.LOW: trading_setup.low_price,
            self.CLOSE: trading_setup.close_price,
            self.ENTRY: trading_setup.entry_mark
        }

        self._exit_specified: bool = False
        if trading_setup.dynamic_exit is not None:
            ohlc_series[self.EXIT] = trading_setup.dynamic_exit
            self._exit_specified = True
        

        self._ohlc: pd.DataFrame = pd.DataFrame(ohlc_series)

        self._profit_precision = 2  # TODO move this to a prameter or constant

    def compute(self) -> pd.DataFrame:
        """
        Wraps the apply function to calculate the trades to simplify the user interface.

        Returns:
            pd.DataFrame: Dataframe witht the trades calculated
        """

        entry_only: pd.Series = self._ohlc[(self._ohlc.entry == 1)].copy(deep=True)

        trades = entry_only.apply(self._calculate_exit,
                                  args=(
                                      self._trading_setup.stop_loss_width,
                                      self._trading_setup.take_profit_width,
                                      self._trading_setup.trade_side,
                                      self._trading_setup.pip_decimal_position,
                                      self._trading_setup.time_barrier_periods
                                  ),
                                  axis=1
                                  )
        self.trades = trades
        return trades        

    def _calculate_exit(self,
                        row: any,
                        stop_loss_width: float,
                        take_profit_width: float,
                        trade_side: TradeSide,
                        pip_decimal_position: int,
                        time_barrier_periods: int):
        try:
            box_setup = Orders()

            box_setup.open_time = str(row.name)
            box_setup.open_price = self._ohlc.loc[box_setup.open_time].open
            box_setup.take_profit_width = take_profit_width
            box_setup.stop_loss_width = stop_loss_width

            max_period_limit: int = min(time_barrier_periods, len(self._ohlc[box_setup.open_time:].index) - 1)

            box_setup.time_limit = self._ohlc[box_setup.open_time:].index[max_period_limit]
            box_setup.trade_side = trade_side
            box_setup.pip_decimal_position = pip_decimal_position

            dynamic_exit: pd.DataFrame | None = None
            if self._trading_setup.dynamic_exit is not None:
                dynamic_exit = self._ohlc[const.EXIT]

            barrier_builder = Labeler(open_price=self._ohlc[const.OPEN],
                                      high_price=self._ohlc[const.HIGH],
                                      low_price=self._ohlc[const.LOW],
                                      close_price=self._ohlc[const.CLOSE],
                                      dynamic_exit=dynamic_exit,
                                      box_setup=box_setup
                                      )
            barrier_builder.compute()

            row["close-price"] = barrier_builder.orders_hit.first_hit.level
            row["close-datetime"] = barrier_builder.orders_hit.first_hit.hit_datetime
            row["close-type"] = barrier_builder.orders_hit.first_hit.order_type.value
            row["profit"] = (trade_side.value * (
                    row["close-price"] - row["open"]) * 10 ** self._trading_setup.pip_decimal_position).__round__(
                self._profit_precision)

        except KeyError as e:
            print("Key error:", e)

        return row


    def plot(self, 
             trade_date: datetime, 
             plot_periods: int = 30,
             overlay_features: list | None = None,
             oscillator_features: list | None = None,
             save_plot: bool = False,
             plot_folder: str = "./",
             periods_before: int = 5,
             periods_after: int = 5) -> None:
        """
        Plot a trade for the specific date
        
        :param trade_date: datetime of the trade to plot
        :param plot_periods: number of periods to plot
        :param overlay_features: list of features to overlay on the plot
        :param oscilators: list of oscilators to plot in the second panel
        :param save_plot: boolean to save the plot (or plot it to the output if false)
        :param plot_folder: folder to save the plot if save_plot is True, default is "./"
        
        :return: None
        """
        # setup barrier builder
        box_setup = Orders()
        box_setup.open_time = trade_date
        box_setup.open_price = self._ohlc.loc[box_setup.open_time].open
        box_setup.take_profit_width = self._trading_setup.take_profit_width
        box_setup.stop_loss_width = self._trading_setup.stop_loss_width
        box_setup.time_limit = self._ohlc[box_setup.open_time:].index[self._trading_setup.time_barrier_periods]
        box_setup.trade_side = self._trading_setup.trade_side
        box_setup.pip_decimal_position =  self._trading_setup.pip_decimal_position
        
        
        # compute barrier builder
        
        barrier_builder = Labeler(open_price=self._ohlc.open,
                               high_price=self._ohlc.high,
                               low_price=self._ohlc.low,
                               close_price=self._ohlc.close,
                               dynamic_exit=self._ohlc[self.EXIT] if self._exit_specified in self._ohlc.columns else None,
                               box_setup=box_setup
                               )
        
        barrier_builder.compute()
                
        # plot the trade
                
        plot_tb = PlotTripleBarrier(open_price=self._ohlc.open,
                           high_price=self._ohlc.high,
                           low_price=self._ohlc.low,
                           close_price=self._ohlc.close,
                           pip_decimal_position=self._trading_setup.pip_decimal_position,
                           overlay_features=overlay_features,
                           oscillator_features=oscillator_features,
                           save_plot=save_plot,
                           plot_folder=plot_folder,
                           periods_after=periods_after,
                           periods_before=periods_before
                           )
        
        plot_tb.plot_multi_barrier(barrier_builder)        
                
        