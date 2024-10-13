"""
This class implements am abstraction for applying a trading setup on
a Pandas dataset

"""

from dataclasses import dataclass
import pandas as pd

from .trade_labeling import TradeSide
from .orders import Orders
from .trade_labeling import Labeler


@dataclass
class TradingParameters:
    entry_column: pd.Series
    stop_loss_width: float
    take_profit_width: float
    trade_side: TradeSide
    pip_decimal_position: int
    time_barrier_periods: int
    dynamic_exit: pd.Series


class DataSetLabeler:
    """
    Class that makes abstraction of executing an apply function
    on a Pandas dataset, avoiding the user some validations.
    """

    def __init__(self,
                 open: pd.Series,
                 high: pd.Series,
                 low: pd.Series,
                 close: pd.Series
                 ):
        self._ohlc: pd.DataFrame = pd.DataFrame([open, high, low, close])

    def compute(self, trade_parameters: TradingParameters):
        # TODO: Implement this methd with the apply on the pandas dataset 
        pass

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
            box_setup.open_price = self._ohlc.loc[box_setup.open_time][self._ohlc.columns[0]]
            box_setup.take_profit_width = take_profit_width
            box_setup.stop_loss_width = stop_loss_width
            max_period_limit: int = min(time_barrier_periods, len(self._ohlc[box_setup.open_time:].index) - 1)

            box_setup.time_limit = self._ohlc[box_setup.open_time:].index[max_period_limit]
            box_setup.trade_side = trade_side
            box_setup.pip_decimal_position = pip_decimal_position

            barrier_builder = Labeler(open_price=self._ohlc[self._ohlc.columns[0]],
                                      high_price=self._ohlc[self._ohlc.columns[1]],
                                      low_price=self._ohlc[self._ohlc.columns[2]],
                                      close_price=self._ohlc[self._ohlc.columns[3]],
                                      dynamic_exit=self._ohlc["exit"],
                                      box_setup=box_setup
                                      )
            barrier_builder.compute()

            row["close-price"] = barrier_builder.orders_hit.first_hit.level
            row["close-datetime"] = barrier_builder.orders_hit.first_hit.hit_datetime
            row["close-type"] = barrier_builder.orders_hit.first_hit.order_type.value

        except Exception as exp_instance:
            print(str(exp_instance))

        return row
