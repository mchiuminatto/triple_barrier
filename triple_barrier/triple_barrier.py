from datetime import datetime
from enum import Enum
from dateutil import parser

import pandas as pd


class BarrierType(Enum):
    TAKE_PROFIT = "take-profit"
    STOP_LOSS = "stop-loss"
    TIME_BARRIER = "time-barrier"
    DYNAMIC = "dynamic"


class CloseEvent(Enum):
    TAKE_PROFIT_HIT = "take-profit-hit"
    STOP_LOSS_HIT = "stop-loss-hit"
    TIME_BARRIER_HIT = "tme-barrier-hit"
    DYNAMIC_BARRIER_HIT = "dynamic-barrier-hit"


class TradeSide(Enum):
    BUY = 1
    SELL = -1


class TripleBarrier:
    def __init__(self) -> None:
        self.open_datetime: datetime | None = None
        self.open_price: float | None = None
        self.stop_loss_level: float | None = None
        self.take_profit_level: float | None = None

        self.trade_side: TradeSide | None = None

        self.stop_loss_pips: float | None = None
        self.take_profit_pips: float | None = None

        self.stop_loss_decimal: float | None = None
        self.take_profit_decimal: float | None = None

        self.time_barrier_date: datetime | None = None
        self.time_barrier_periods: int | None = None

        self.stop_loss_hit_datetime: datetime | None = None
        self.take_profit_hit_datetime: datetime | None = None
        self.dynamic_condition_hit: datetime | None = None

        self.close_time: datetime | None = None
        self.close_event: CloseEvent | None = None


class Barrier:

    def __init__(self,
                 level: float | None = None,
                 hit_datetime: datetime | None = None
                 ):
        self.level: float | None = level
        self.hit_datetime: datetime | None = hit_datetime


class TripleBarrierBuilder:

    def __init__(self,
                 open: pd.Series,
                 high: pd.Series,
                 low: pd.Series,
                 close: pd.Series,
                 trade_open_datetime: str,
                 take_profit_pips: float,
                 stop_loss_pips: float,
                 time_barrier_periods: int,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 dynamic_barrier_function: object = None
                 ) -> None:
        self.open: pd.Series = open
        self.high: pd.Series = high
        self.low: pd.Series = low
        self.close: pd.Series = close

        self.triple_barrier: TripleBarrier = TripleBarrier()
        self.triple_barrier.open_datetime = parser.parse(trade_open_datetime)
        self.triple_barrier.take_profit_pips = take_profit_pips
        self.triple_barrier.stop_loss_pips = stop_loss_pips
        self.triple_barrier.time_barrier_periods = time_barrier_periods
        self.triple_barrier.trade_side = trade_side
        self.triple_barrier.stop_loss_decimal = stop_loss_pips * 10 ** -pip_decimal_position
        self.triple_barrier.take_profit_decimal = take_profit_pips * 10 ** -pip_decimal_position

        self.dynamic_barrier: object = dynamic_barrier_function

    def compute(self):
        ...

    def compute_take_profit_level(self) -> datetime:
        ...

    def calculate_next_take_profit_hit(self) -> datetime:
        ...

    def calculate_time_barrier_hit(self) -> datetime:
        ...

    def calculate_dynamic_barrier_hit(self) -> datetime:
        ...


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
        self._pip_factor: float = 10 ** (-pip_decimal_position)
        self._pip_decimal_position: int = pip_decimal_position

        if take_profit_width is not None:
            self._take_profit_decimal: float = take_profit_width * self._pip_factor
        self._take_profit_level = take_profit_level

        self.barrier: Barrier = Barrier()

        self._take_profit_level: float | None = None

    def _compute_take_profit_level(self):

        if self._take_profit_level is None:
            trade_open_price = self._open_price[self._open_datetime]
            if self._trade_side == TradeSide.BUY:
                self.barrier.level = (trade_open_price + self._take_profit_decimal).round(
                    self._pip_decimal_position + 1)
            else:
                self.barrier.level = (trade_open_price - self._take_profit_decimal).round(
                    self._pip_decimal_position + 1)

    def _compute_next_take_profit_hit(self):

        high = self._high_price[self._open_datetime:]
        low = self._low_price[self._open_datetime:]

        if self._trade_side == TradeSide.BUY:
            mask_level_hit = high > self.barrier.level
            hit_date = high[mask_level_hit].index[0]
        else:
            mask_level_hit = low < self.barrier.level
            hit_date = low[mask_level_hit].index[0]

        self.barrier.hit_datetime = datetime.fromtimestamp(datetime.timestamp(hit_date))

    def compute(self) -> Barrier:
        self._compute_take_profit_level()
        self._compute_next_take_profit_hit()
        return self.barrier


class StopLoss:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 open_datetime: str,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 stop_loss_width: float | None = None,
                 stop_loss_level: float | None = None
                 ):

        self._open_price: pd.Series = open_price
        self._high_price: pd.Series = high_price
        self._low_price: pd.Series = low_price
        self._close_price: pd.Series = close_price
        self._open_datetime: str = open_datetime
        self._trade_side: TradeSide = trade_side
        self._pip_factor: float = 10 ** (-pip_decimal_position)
        self._pip_decimal_position: int = pip_decimal_position

        if stop_loss_width is not None:
            self._stop_loss_decimal: float = stop_loss_width * self._pip_factor
        self._take_profit_level = stop_loss_level

        self.barrier: Barrier = Barrier()

        self._take_profit_level: float | None = None

    def _compute_stop_loss_level(self):

        if self._take_profit_level is None:
            trade_open_price = self._open_price[self._open_datetime]
            if self._trade_side == TradeSide.BUY:
                self.barrier.level = (trade_open_price - self._stop_loss_decimal).round(self._pip_decimal_position + 1)
            else:
                self.barrier.level = (trade_open_price + self._stop_loss_decimal).round(self._pip_decimal_position + 1)

    def _compute_next_level_hit(self):

        high = self._high_price[self._open_datetime:]
        low = self._low_price[self._open_datetime:]

        if self._trade_side == TradeSide.BUY:
            mask_level_hit = low <= self.barrier.level
            hit_date = high[mask_level_hit].index[0]
        else:
            mask_level_hit = high >= self.barrier.level
            hit_date = low[mask_level_hit].index[0]

        self.barrier.hit_datetime = datetime.fromtimestamp(datetime.timestamp(hit_date))

    def compute(self) -> Barrier:
        self._compute_stop_loss_level()
        self._compute_next_level_hit()
        return self.barrier


class TimeBarrier:

    def __init__(self,
                 close_price: pd.Series,
                 time_barrier_periods: int,
                 open_datetime: str):
        self.close_price: pd.Series = close_price
        self.time_barrier_periods: int = time_barrier_periods
        self.open_datetime: str = open_datetime

        self.barrier = Barrier()

    def _compute_hit_date_time(self):
        close_price = self.close_price[self.open_datetime:]
        self.barrier.hit_datetime = close_price.shift(-self.time_barrier_periods).index[0]

    def _compute_hit_level(self):
        close_price = self.close_price[self.open_datetime:]
        self.barrier.level = close_price.shift(-self.time_barrier_periods).iloc[0]

    def compute(self) -> Barrier:
        self._compute_hit_date_time()
        self._compute_hit_level()
        return self.barrier


class DynamicBarrier:

    def __init__(self,
                 open_price: pd.Series,
                 exit_signals: pd.Series,
                 open_datetime: str,
                 ):
        self.open_price = open_price
        self.open_datetime: str = open_datetime
        self.exit_signals: pd.Series = exit_signals

        self.barrier: Barrier = Barrier()

    def compute(self):
        self._compute_hit_datetime()
        self._compute_hit_level()
        return self.barrier

    def _compute_hit_datetime(self):
        trade_exit_signals: pd.Series = self.exit_signals[self.open_datetime:]
        mask_exit = trade_exit_signals == 1
        self.barrier.hit_datetime = trade_exit_signals[mask_exit].index[0]

    def _compute_hit_level(self):
        open_price: pd.Series = self.open_price[self.open_datetime:]
        trade_exit_signals: pd.Series = self.exit_signals[self.open_datetime:]
        mask_exit = trade_exit_signals == 1
        self.barrier.level = open_price[mask_exit].iloc[0]

