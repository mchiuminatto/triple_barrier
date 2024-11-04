"""
Class that calculates a single trade result based on the order setup specified by the
following parameters

- stop loss
- take profit
- expiration date or periods
- dynamic exit

It calculates the trade result starting form a datetime (opening datetime) to finally get
a hit datetime and hit price based on the parameters described above.

"""

from datetime import datetime

import pandas as pd
import numpy as np

from triple_barrier import constants
from triple_barrier.orders import BoxBuilder
from triple_barrier.orders import Orders
from triple_barrier.orders import OrdersBox
from triple_barrier.types import OrderBoxHits
from triple_barrier.types import OrderHit
from triple_barrier.types import OrderType
from triple_barrier.types import TradeSide


class Labeler:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 # TODO: Move the box_setup to the compute method
                 box_setup: Orders,
                 dynamic_exit: pd.Series | None = None
                 ) -> None:

        self.open: pd.Series = open_price
        self.high: pd.Series = high_price
        self.low: pd.Series = low_price
        self.close: pd.Series = close_price
        self.dynamic_exit: pd.Series = dynamic_exit

        box_builder: BoxBuilder = BoxBuilder()
        self.multi_barrier_box: OrdersBox = box_builder.build_multi_barrier_box(box_setup)

        self.orders_hit: OrderBoxHits = OrderBoxHits()

        self._take_profit_barrier: TakeProfit | None = None
        self._stop_loss_barrier: StopLoss | None = None
        self._time_barrier: TimeBarrier | None = None
        self._dynamic_barrier: DynamicOrder | None = None

        self._do_initializations()

    def _do_initializations(self):
        self._take_profit_barrier = TakeProfit(open_price=self.open,
                                               high_price=self.high,
                                               low_price=self.low,
                                               close_price=self.close,
                                               open_datetime=self.multi_barrier_box.open_datetime,
                                               trade_side=self.multi_barrier_box.trade_side,
                                               pip_decimal_position=self.multi_barrier_box.pip_decimal_position,
                                               take_profit=self.multi_barrier_box.take_profit
                                               )
        self._stop_loss_barrier = StopLoss(open_price=self.open,
                                           high_price=self.high,
                                           low_price=self.low,
                                           close_price=self.close,
                                           open_datetime=self.multi_barrier_box.open_datetime,
                                           trade_side=self.multi_barrier_box.trade_side,
                                           pip_decimal_position=self.multi_barrier_box.pip_decimal_position,
                                           stop_loss=self.multi_barrier_box.stop_loss
                                           )
        self._time_barrier = TimeBarrier(open_price=self.open,
                                         time_limit_date=self.multi_barrier_box.time_limit,
                                         open_datetime=self.multi_barrier_box.open_datetime
                                         )
        self._dynamic_barrier = DynamicOrder(open_price=self.open,
                                             exit_signals=self.dynamic_exit,
                                             open_datetime=self.multi_barrier_box.open_datetime
                                             )

    def compute(self) -> OrderBoxHits:
        """
        Calculates the close price for a trade based on the order setup specified in the box_setup.

        :param
        box_setup: Is a structure that contains all the hits in the barriers (orders) and the first one
        to occur.

        :return:
        order_hit: Structure returning all the barriers hists and the first one to occur.
        """

        self._compute_take_profit_barrier()
        self._compute_stop_loss_barrier()
        self._compute_time_barrier()
        if self.dynamic_exit is not None:
            self._compute_dynamic_barrier()
        self._select_first_hit()
        return self.orders_hit

    def _compute_take_profit_barrier(self):

        self._take_profit_barrier.compute()
        self.orders_hit.barriers.append(self._take_profit_barrier.barrier)

    def _compute_stop_loss_barrier(self):

        self._stop_loss_barrier.compute()
        self.orders_hit.barriers.append(self._stop_loss_barrier.barrier)

    def _compute_time_barrier(self):

        self._time_barrier.compute()
        self.orders_hit.barriers.append(self._time_barrier.barrier)

    def _compute_dynamic_barrier(self):

        self._dynamic_barrier.compute()
        self.orders_hit.barriers.append(self._dynamic_barrier.barrier)

    def _select_first_hit(self):
        first_hit: OrderHit | None = None
        for barrier in self.orders_hit.barriers:
            if first_hit is None:
                first_hit = barrier
            else:
                if barrier.hit_datetime < first_hit.hit_datetime:
                    first_hit = barrier
        self.orders_hit.first_hit = first_hit


class TakeProfit:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 open_datetime: datetime,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 take_profit: float | None = None
                 ):

        self._open_price: pd.Series = open_price
        self._high_price: pd.Series = high_price
        self._low_price: pd.Series = low_price
        self._close_price: pd.Series = close_price
        self._open_datetime: datetime = open_datetime
        self._trade_side: TradeSide = trade_side
        self._pip_decimal_position: int = pip_decimal_position

        self.barrier: OrderHit = OrderHit(order_type=OrderType.TAKE_PROFIT,
                                          level=take_profit)

    def compute(self):
        self._compute_next_take_profit_hit()

    def _compute_next_take_profit_hit(self):

        hit_date: datetime | None = constants.INFINITE_DATE

        if self.barrier.level != self._trade_side.value * np.inf:

            high = self._high_price[self._open_datetime:]
            low = self._low_price[self._open_datetime:]

            if self._trade_side == TradeSide.BUY:
                mask_level_hit = high >= self.barrier.level
                if len(high[mask_level_hit] != 0):
                    hit_date = high[mask_level_hit].index[0]
            else:
                mask_level_hit = low <= self.barrier.level
                if len(low[mask_level_hit]) != 0:
                    hit_date = low[mask_level_hit].index[0]

        self.barrier.hit_datetime = datetime.fromtimestamp(datetime.timestamp(hit_date))


class StopLoss:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 open_datetime: datetime,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 stop_loss: float = None
                 ):

        self._open_price: pd.Series = open_price
        self._high_price: pd.Series = high_price
        self._low_price: pd.Series = low_price
        self._close_price: pd.Series = close_price
        self._open_datetime: datetime = open_datetime
        self._trade_side: TradeSide = trade_side
        self._pip_decimal_position: int = pip_decimal_position

        self.barrier: OrderHit = OrderHit(order_type=OrderType.STOP_LOSS,
                                          level=stop_loss)

    def compute(self):
        self._compute_next_level_hit()

    def _compute_next_level_hit(self):

        hit_datetime: datetime = constants.INFINITE_DATE

        if self.barrier.level != -self._trade_side.value * np.inf:
            high = self._high_price[self._open_datetime:]
            low = self._low_price[self._open_datetime:]

            if self._trade_side == TradeSide.BUY:
                mask_level_hit = low <= self.barrier.level
                if len(low[mask_level_hit]) != 0:
                    hit_datetime = high[mask_level_hit].index[0]
            else:
                mask_level_hit = high >= self.barrier.level
                if len(high[mask_level_hit] != 0):
                    hit_datetime = low[mask_level_hit].index[0]

        self.barrier.hit_datetime = datetime.fromtimestamp(datetime.timestamp(hit_datetime))


class TimeBarrier:
    # TODO: deal with no time barrier
    # TODO: deal with time barrier beyond last time series date

    def __init__(self,
                 open_price: pd.Series,
                 time_limit_date: datetime,
                 open_datetime: datetime):
        self.open_price: pd.Series = open_price
        self.open_datetime: datetime = open_datetime

        expiration_datetime: datetime

        if time_limit_date > open_price.index[-1]:
            expiration_datetime: datetime = constants.INFINITE_DATE
        else:
            expiration_datetime = time_limit_date

        self.barrier = OrderHit(order_type=OrderType.TIME_EXPIRATION, hit_datetime=expiration_datetime)

    def compute(self):
        self._compute_hit_level()

    def _compute_hit_level(self):
        hit_level: float = np.inf

        open_price = self.open_price[self.open_datetime:]
        if self.barrier.hit_datetime != constants.INFINITE_DATE:
            hit_level = open_price[self.barrier.hit_datetime:].iloc[0]

        self.barrier.level = hit_level


class DynamicOrder:

    def __init__(self,
                 open_price: pd.Series,
                 exit_signals: pd.Series,
                 open_datetime: datetime,
                 ):
        self.open_price = open_price
        self.open_datetime: datetime = open_datetime
        self.exit_signals: pd.Series = exit_signals

        self.barrier: OrderHit = OrderHit(order_type=OrderType.DYNAMIC)

    def compute(self):
        self._compute_hit_datetime()
        self._compute_hit_level()

    def _compute_hit_datetime(self):

        hit_datetime: datetime = constants.INFINITE_DATE
        trade_exit_signals: pd.Series = self.exit_signals[self.open_datetime:]
        mask_exit = trade_exit_signals == 1
        if len(trade_exit_signals[mask_exit]) != 0:
            hit_datetime = trade_exit_signals[mask_exit].index[0]

        self.barrier.hit_datetime = hit_datetime

    def _compute_hit_level(self):
        hit_level: float = np.inf
        if self.barrier.hit_datetime != constants.INFINITE_DATE:
            open_price: pd.Series = self.open_price[self.open_datetime:]
            trade_exit_signals: pd.Series = self.exit_signals[self.open_datetime:]
            mask_exit = trade_exit_signals == 1
            hit_trigger_date: datetime = open_price[mask_exit].index[0]
            hit_level = open_price[hit_trigger_date:].iloc[1]

        self.barrier.level = hit_level
