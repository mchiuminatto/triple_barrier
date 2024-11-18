"""
This class implements am abstraction for applying a trading setup on
a Pandas dataset

"""

from dataclasses import dataclass
import pandas as pd

from .trade_labeling import TradeSide
from .orders import Orders
from .trade_labeling import Labeler
import triple_barrier.constants as const


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
    on a Pandas dataset, avoiding the user some validations.
    """

    def __init__(self, trading_setup: TradingParameters):

        self._trading_setup = trading_setup

        ohlc_series: dict = {
            "open": trading_setup.open_price,
            "high": trading_setup.high_price,
            "low": trading_setup.low_price,
            "close": trading_setup.close_price,
            "entry": trading_setup.entry_mark
        }

        if trading_setup.dynamic_exit is not None:
            ohlc_series["exit"] = trading_setup.dynamic_exit

        self._ohlc: pd.DataFrame = pd.DataFrame(ohlc_series)

        self._profit_precision = 2

    def compute(self) -> pd.DataFrame:

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

        # TODO: remove this
        except Exception as exp_instance:
            print(str(exp_instance))

        return row
