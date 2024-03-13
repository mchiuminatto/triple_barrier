"""
Implements a Builder parameter for the MultiBarrierBox
"""

from datetime import datetime

import pandas as pd

from triple_barrier.multi_barrier_types import TradeSide


class MultiBarrierParameters:

    def __init__(self):
        self.open_time: str | None = None
        self.open_price: float | None = None
        self.trade_side: TradeSide | None = None
        self.take_profit_width: float | None = None
        self.take_profit_level: float | None = None
        self.stop_loss_width: float | None = None
        self.stop_loss_level: float | None = None
        self.time_limit: str | None = None
        self.pip_decimal_position: int | None = None


class MultiBarrierBox:

    def __init__(self,
                 trade_side: TradeSide,
                 open_datetime: datetime,
                 open_price: float,
                 stop_loss: float,
                 take_profit: float,
                 time_limit: datetime,
                 pip_decimal_position: int
                 ):

        self.open_datetime: datetime = open_datetime
        self.open_price: float = open_price
        self.stop_loss: float = stop_loss
        self.take_profit: float = take_profit
        self.trade_side: TradeSide = trade_side
        self.time_limit: datetime = time_limit
        self.pip_decimal_position = pip_decimal_position

    def __str__(self):
        output: str = f"""
        Open datetime: {self.open_datetime}
        Open price: {self.open_price}
        Stop loss: {self.stop_loss}
        Take profit : {self.take_profit}
        Trade side: {self.trade_side}
        Time limit: {self.time_limit}
        Pip position: {self.pip_decimal_position} 
        """

        return output


class BoxBuilder:

    def __init__(self):
        self._open_datetime: datetime | None = None
        self._open_price: float | None = None
        self._stop_loss: float | None = None
        self._take_profit: float | None = None
        self._trade_side: TradeSide | None = None
        self._time_limit: datetime | None = None
        self._pip_decimal_position: int | None = None

    def build_multi_barrier_box(self,
                                multi_barrier_parameters: MultiBarrierParameters
                                ) -> MultiBarrierBox:

        self.open_date_time(multi_barrier_parameters.open_time)
        self.open_price(multi_barrier_parameters.open_price)
        self.trade_side(multi_barrier_parameters.trade_side)
        self.take_profit(multi_barrier_parameters.trade_side,
                         multi_barrier_parameters.open_price,
                         multi_barrier_parameters.take_profit_width,
                         multi_barrier_parameters.take_profit_level,
                         multi_barrier_parameters.pip_decimal_position)
        self.stop_loss(multi_barrier_parameters.trade_side,
                       multi_barrier_parameters.open_price,
                       multi_barrier_parameters.stop_loss_width,
                       multi_barrier_parameters.stop_loss_level,
                       multi_barrier_parameters.pip_decimal_position)
        self.time_limit(multi_barrier_parameters.time_limit)
        self.pip_decimal_position(multi_barrier_parameters.pip_decimal_position)
        return MultiBarrierBox(self._trade_side,
                               self._open_datetime,
                               self._open_price,
                               self._stop_loss,
                               self._take_profit,
                               self._time_limit,
                               self._pip_decimal_position)

    def open_date_time(self, open_date_time: str):
        self._open_datetime = pd.to_datetime(open_date_time)

    def open_price(self, open_price: float):
        self._open_price = open_price

    def stop_loss(self,
                  trade_side: TradeSide,
                  open_price: float,
                  stop_loss_width: float = None,
                  stop_loss_level: float = None,
                  pip_decimal_position: float = None):

        if stop_loss_width is not None and stop_loss_level is not None:
            raise ValueError("Either stop_loss_level or stop_loss_width can be specified but not both")
        if pip_decimal_position is None:
            raise ValueError("You need to specify pip_factor")
        if stop_loss_width is not None:
            self._stop_loss = open_price - trade_side.value*stop_loss_width*(10**-pip_decimal_position)
        elif stop_loss_level is not None:
            self._stop_loss = stop_loss_level
        else:
            raise ValueError("Neither stop_loss_level or stop_loss_width were passed as parameter")

    def take_profit(self,
                    trade_side: TradeSide,
                    open_price: float,
                    take_profit_width: float = None,
                    take_profit_level: float = None,
                    pip_decimal_position: float = None):
        if take_profit_level is None and take_profit_width is None:
            raise ValueError("Either take_profit_level or take_profit_width can be specified but not both")

        if pip_decimal_position is None:
            raise ValueError("You need to specify pip_decimal_position")

        if take_profit_width is not None:
            self._take_profit = open_price + trade_side.value*take_profit_width*(10**-pip_decimal_position)
        elif take_profit_level is not None:
            self._take_profit = take_profit_level
        else:
            raise ValueError("You need to pass take_level or take_profit_width as parameter")

    def trade_side(self,
                   trade_side: TradeSide):
        self._trade_side = trade_side

    def time_limit(self,
                   time_limit_datetime: str
                   ):

        self._time_limit = pd.to_datetime(time_limit_datetime)

    def pip_decimal_position(self, pip_decimal_position: int):
        self._pip_decimal_position = pip_decimal_position


