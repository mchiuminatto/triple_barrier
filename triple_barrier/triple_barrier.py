from datetime import datetime
from enum import Enum

import pandas as pd
import numpy as np

from triple_barrier import constants
from triple_barrier.multi_barrier_box import BoxBuilder
from triple_barrier.multi_barrier_box import MultiBarrierParameters
from triple_barrier.multi_barrier_box import MultiBarrierBox
from triple_barrier.multi_barrier_types import MultiBarrierHit
from triple_barrier.multi_barrier_types import BarrierHit
from triple_barrier.multi_barrier_types import BarrierType
from triple_barrier.multi_barrier_types import TradeSide


class MultiBarrier:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 box_setup: MultiBarrierParameters,
                 dynamic_exit: pd.Series | None = None
                 ) -> None:

        self.open: pd.Series = open_price
        self.high: pd.Series = high_price
        self.low: pd.Series = low_price
        self.close: pd.Series = close_price
        self.dynamic_exit: pd.Series = dynamic_exit

        box_builder: BoxBuilder = BoxBuilder()
        self.multi_barrier_box: MultiBarrierBox = box_builder.build_multi_barrier_box(box_setup)

        self.multi_barrier_hit: MultiBarrierHit = MultiBarrierHit()

    def compute(self):
        try:
            self._compute_take_profit_barrier()
            self._compute_stop_loss_barrier()
            self._compute_time_barrier()
            if self.dynamic_exit is not None:
                self._compute_dynamic_barrier()
            self._select_first_hit()
            return self.multi_barrier_hit
        except Exception as error_instance:
            raise Exception(str(error_instance))

    def _compute_take_profit_barrier(self):
        take_profit_barrier: TakeProfit = TakeProfit(open_price=self.open,
                                                     high_price=self.high,
                                                     low_price=self.low,
                                                     close_price=self.close,
                                                     open_datetime=self.multi_barrier_box.open_datetime,
                                                     trade_side=self.multi_barrier_box.trade_side,
                                                     pip_decimal_position=self.multi_barrier_box.pip_decimal_position,
                                                     take_profit=self.multi_barrier_box.take_profit
                                                     )
        take_profit_barrier.compute()
        self.multi_barrier_hit.barriers.append(take_profit_barrier.barrier)

    def _compute_stop_loss_barrier(self):
        stop_loss_barrier: StopLoss = StopLoss(open_price=self.open,
                                               high_price=self.high,
                                               low_price=self.low,
                                               close_price=self.close,
                                               open_datetime=self.multi_barrier_box.open_datetime,
                                               trade_side=self.multi_barrier_box.trade_side,
                                               pip_decimal_position=self.multi_barrier_box.pip_decimal_position,
                                               stop_loss=self.multi_barrier_box.stop_loss
                                               )
        stop_loss_barrier.compute()
        self.multi_barrier_hit.barriers.append(stop_loss_barrier.barrier)

    def _compute_time_barrier(self):
        time_barrier: TimeBarrier = TimeBarrier(close_price=self.close,
                                                time_limit_date=self.multi_barrier_box.time_limit,
                                                open_datetime=self.multi_barrier_box.open_datetime
                                                )
        time_barrier.compute()
        self.multi_barrier_hit.barriers.append(time_barrier.barrier)

    def _compute_dynamic_barrier(self):
        dynamic_barrier: DynamicBarrier = DynamicBarrier(close_price=self.close,
                                                         exit_signals=self.dynamic_exit,
                                                         open_datetime=self.multi_barrier_box.open_datetime
                                                         )
        dynamic_barrier.compute()
        self.multi_barrier_hit.barriers.append(dynamic_barrier.barrier)

    def _select_first_hit(self):
        first_hit: BarrierHit | None = None
        for barrier in self.multi_barrier_hit.barriers:
            if first_hit is None:
                first_hit = barrier
            else:
                if barrier.hit_datetime < first_hit.hit_datetime:
                    first_hit = barrier
        self.multi_barrier_hit.first_hit = first_hit


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

        self.barrier: BarrierHit = BarrierHit(barrier_type=BarrierType.TAKE_PROFIT,
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

        self.barrier: BarrierHit = BarrierHit(barrier_type=BarrierType.STOP_LOSS,
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
                 close_price: pd.Series,
                 time_limit_date: datetime,
                 open_datetime: datetime):
        self.close_price: pd.Series = close_price
        self.open_datetime: datetime = open_datetime

        self.barrier = BarrierHit(barrier_type=BarrierType.TIME_BARRIER, hit_datetime=time_limit_date)

    def compute(self):
        self._compute_hit_level()

    def _compute_hit_level(self):
        hit_level: float = np.inf

        close_price = self.close_price[self.open_datetime:]
        if self.barrier.hit_datetime != constants.INFINITE_DATE:
            hit_level = close_price[self.barrier.hit_datetime]

        self.barrier.level = hit_level


class DynamicBarrier:

    def __init__(self,
                 close_price: pd.Series,
                 exit_signals: pd.Series,
                 open_datetime: datetime,
                 ):
        self.close_price = close_price
        self.open_datetime: datetime = open_datetime
        self.exit_signals: pd.Series = exit_signals

        self.barrier: BarrierHit = BarrierHit(barrier_type=BarrierType.DYNAMIC)

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
            close_price: pd.Series = self.close_price[self.open_datetime:]
            trade_exit_signals: pd.Series = self.exit_signals[self.open_datetime:]
            mask_exit = trade_exit_signals == 1
            hit_level = close_price[mask_exit].iloc[0]

        self.barrier.level = hit_level
