from datetime import datetime
from enum import Enum

import pandas as pd
import numpy as np

from triple_barrier import constants


class BarrierType(Enum):
    TAKE_PROFIT = "take-profit"
    STOP_LOSS = "stop-loss"
    TIME_BARRIER = "time-barrier"
    DYNAMIC = "dynamic"


class ExitType(Enum):
    TAKE_PROFIT_HIT = "take-profit-hit"
    STOP_LOSS_HIT = "stop-loss-hit"
    TIME_BARRIER_HIT = "tme-barrier-hit"
    DYNAMIC_BARRIER_HIT = "dynamic-barrier-hit"


class TradeSide(Enum):
    BUY = 1
    SELL = -1


class MultiBarrier:
    def __init__(self) -> None:
        self.barriers: list[BarrierHit] = []
        self.first_hit: BarrierHit = BarrierHit()


class BarrierHit:

    def __init__(self,
                 level: float | None = None,
                 hit_datetime: datetime | None = None,
                 barrier_type: BarrierType | None = None
                 ):
        self.level: float = level
        self.hit_datetime: datetime = hit_datetime
        self.barrier_type: BarrierType = barrier_type


class MultiBarrierBuilder:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 trade_open_datetime: str,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 take_profit_pips: float = None,
                 take_profit_level: float | None = None,
                 stop_loss_pips: float | None = None,
                 stop_loss_level: float | None = None,
                 time_barrier_periods: int = np.inf,
                 dynamic_exit: pd.Series | None = None
                 ) -> None:

        self.open: pd.Series = open_price
        self.high: pd.Series = high_price
        self.low: pd.Series = low_price
        self.close: pd.Series = close_price

        self.multi_barrier: MultiBarrier = MultiBarrier()
        self.open_datetime: str = trade_open_datetime

        self.take_profit_pips: float = take_profit_pips
        self.take_profit_level: float = take_profit_level

        self.stop_loss_pips: float = stop_loss_pips
        self.stop_loss_level: float = stop_loss_level

        self.time_barrier_periods: int = time_barrier_periods
        self.trade_side: TradeSide = trade_side
        self.pip_decimal_position: int = pip_decimal_position

        self.dynamic_exit: pd.Series = dynamic_exit

    def compute(self):
        try:
            self.compute_take_profit_barrier()
            self.compute_stop_loss_barrier()
            self.compute_time_barrier()
            if self.dynamic_exit is not None:
                self.compute_dynamic_barrier()
            self.select_first_hit()
        except Exception as error_instance:
            raise Exception(str(error_instance))

    def compute_take_profit_barrier(self):
        take_profit_barrier: TakeProfit = TakeProfit(open_price=self.open,
                                                     high_price=self.high,
                                                     low_price=self.low,
                                                     close_price=self.close,
                                                     open_datetime=self.open_datetime,
                                                     trade_side=self.trade_side,
                                                     pip_decimal_position=self.pip_decimal_position,
                                                     take_profit_width=self.take_profit_pips,
                                                     take_profit_level=self.take_profit_level
                                                     )
        take_profit_barrier.compute()
        self.multi_barrier.barriers.append(take_profit_barrier.barrier)

    def compute_stop_loss_barrier(self):
        stop_loss_barrier: StopLoss = StopLoss(open_price=self.open,
                                               high_price=self.high,
                                               low_price=self.low,
                                               close_price=self.close,
                                               open_datetime=self.open_datetime,
                                               trade_side=self.trade_side,
                                               pip_decimal_position=self.pip_decimal_position,
                                               stop_loss_width=self.stop_loss_pips,
                                               stop_loss_level=self.stop_loss_level
                                               )
        stop_loss_barrier.compute()
        self.multi_barrier.barriers.append(stop_loss_barrier.barrier)

    def compute_time_barrier(self):
        time_barrier: TimeBarrier = TimeBarrier(close_price=self.close,
                                                time_barrier_periods=self.time_barrier_periods,
                                                open_datetime=self.open_datetime
                                                )
        time_barrier.compute()
        self.multi_barrier.barriers.append(time_barrier.barrier)

    def compute_dynamic_barrier(self):
        dynamic_barrier: DynamicBarrier = DynamicBarrier(close_price=self.close,
                                                         exit_signals=self.dynamic_exit,
                                                         open_datetime=self.open_datetime
                                                         )
        dynamic_barrier.compute()
        self.multi_barrier.barriers.append(dynamic_barrier.barrier)

    def select_first_hit(self):
        first_hit: BarrierHit | None = None
        for barrier in self.multi_barrier.barriers:
            if first_hit is None:
                first_hit = barrier
            else:
                if barrier.hit_datetime < first_hit.hit_datetime:
                    first_hit = barrier
        self.multi_barrier.first_hit = first_hit


class TakeProfit:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 open_datetime: str,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 take_profit_width: float | None = None,
                 take_profit_level: float | None = None
                 ):

        self._open_price: pd.Series = open_price
        self._high_price: pd.Series = high_price
        self._low_price: pd.Series = low_price
        self._close_price: pd.Series = close_price
        self._open_datetime: str = open_datetime
        self._trade_side: TradeSide = trade_side
        self._pip_decimal_position: int = pip_decimal_position
        self._take_profit_width: float = take_profit_width
        self._take_profit_level: float = take_profit_level

        self._validate_barrier_parameters()

        self.barrier: BarrierHit = BarrierHit(barrier_type=BarrierType.TAKE_PROFIT,
                                              level=take_profit_level)

    def _validate_barrier_parameters(self):
        if self._take_profit_width is not None and self._take_profit_level is not None:
            raise ValueError("Either take_profit_level or take_profit_with are allowed not both")

    def compute(self):
        self._compute_take_profit_level()
        self._compute_next_take_profit_hit()

    def _compute_take_profit_level(self):
        if self.barrier.level is None:
            barrier_level: float = self._trade_side.value * np.inf
            if self._take_profit_width is not None:
                pip_factor: float = 10 ** (-self._pip_decimal_position)
                take_profit_width_decimal: float = self._take_profit_width * pip_factor
                trade_open_price = self._open_price[self._open_datetime]
                barrier_level = (trade_open_price + self._trade_side.value * take_profit_width_decimal).round(
                    self._pip_decimal_position + 1)
            self.barrier.level = barrier_level

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
                 open_datetime: str,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 stop_loss_width: float = None,
                 stop_loss_level: float = None
                 ):

        self._open_price: pd.Series = open_price
        self._high_price: pd.Series = high_price
        self._low_price: pd.Series = low_price
        self._close_price: pd.Series = close_price
        self._open_datetime: str = open_datetime
        self._trade_side: TradeSide = trade_side
        self._pip_decimal_position: int = pip_decimal_position
        self._stop_loss_width: float = stop_loss_width
        self._stop_loss_level: float = stop_loss_level

        self._validate_barrier_parameters()

        self.barrier: BarrierHit = BarrierHit(barrier_type=BarrierType.STOP_LOSS,
                                              level=stop_loss_level)

    def _validate_barrier_parameters(self):
        if self._stop_loss_width is not None and self._stop_loss_level is not None:
            raise ValueError("Either stop_loss_level or stop_loss_with are allowed not both")

    def compute(self):
        self._compute_stop_loss_level()
        self._compute_next_level_hit()

    def _compute_stop_loss_level(self):
        if self.barrier.level is None:
            barrier_level: float = -self._trade_side.value * np.inf
            if self._stop_loss_width is not None:
                pip_factor: float = 10 ** (-self._pip_decimal_position)
                stop_loss_width_decimal: float = self._stop_loss_width * pip_factor
                trade_open_price = self._open_price[self._open_datetime]
                barrier_level = (trade_open_price - self._trade_side.value * stop_loss_width_decimal).round(
                    self._pip_decimal_position + 1)
            self.barrier.level = barrier_level

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
                 time_barrier_periods: int,
                 open_datetime: str):
        self.close_price: pd.Series = close_price
        self.time_barrier_periods: int = time_barrier_periods
        self.open_datetime: str = open_datetime

        self.barrier = BarrierHit(barrier_type=BarrierType.TIME_BARRIER)

    def compute(self):
        self._compute_hit_date_time()
        self._compute_hit_level()

    def _compute_hit_date_time(self):
        hit_datetime: datetime = constants.INFINITE_DATE

        close_price = self.close_price[self.open_datetime:]
        if len(close_price) >= self.time_barrier_periods + 1:
            hit_datetime = close_price.index[self.time_barrier_periods]

        self.barrier.hit_datetime = hit_datetime

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
                 open_datetime: str,
                 ):
        self.close_price = close_price
        self.open_datetime: str = open_datetime
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
