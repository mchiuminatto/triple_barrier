from datetime import datetime
from enum import Enum
from dateutil import parser

import pandas as pd


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
        self.barriers: list[Barrier] = []
        self.first_hit: Barrier = Barrier()


class Barrier:

    def __init__(self,
                 level: float | None = None,
                 hit_datetime: datetime | None = None,
                 barrier_type: BarrierType | None = None
                 ):
        self.level: float | None = level
        self.hit_datetime: datetime | None = hit_datetime
        self.barrier_type: BarrierType = barrier_type


class MultiBarrierBuilder:

    def __init__(self,
                 open_price: pd.Series,
                 high_price: pd.Series,
                 low_price: pd.Series,
                 close_price: pd.Series,
                 trade_open_datetime: str,
                 take_profit_pips: float,
                 stop_loss_pips: float,
                 time_barrier_periods: int,
                 trade_side: TradeSide,
                 pip_decimal_position: int,
                 dynamic_exit: pd.Series | None = None
                 ) -> None:
        self.open: pd.Series = open_price
        self.high: pd.Series = high_price
        self.low: pd.Series = low_price
        self.close: pd.Series = close_price

        self.multi_barrier: MultiBarrier = MultiBarrier()
        self.open_datetime = trade_open_datetime
        self.take_profit_pips = take_profit_pips
        self.stop_loss_pips = stop_loss_pips
        self.time_barrier_periods = time_barrier_periods
        self.trade_side = trade_side
        self.pip_decimal_position = pip_decimal_position

        self.dynamic_exit: pd.Series = dynamic_exit

    def compute(self):
        self.compute_take_profit_barrier()
        self.compute_stop_loss_barrier()
        self.compute_time_barrier()
        if self.dynamic_exit is not None:
            self.compute_dynamic_barrier()
        self.select_first_hit()

    def compute_take_profit_barrier(self):
        take_profit_barrier: TakeProfit = TakeProfit(open_price=self.open,
                                                     high_price=self.high,
                                                     low_price=self.low,
                                                     close_price=self.close,
                                                     open_datetime=self.open_datetime,
                                                     trade_side=self.trade_side,
                                                     pip_decimal_position=self.pip_decimal_position,
                                                     take_profit_width=self.take_profit_pips,
                                                     )
        take_profit: Barrier = take_profit_barrier.compute()
        self.multi_barrier.barriers.append(take_profit)

    def compute_stop_loss_barrier(self):
        stop_loss_barrier: StopLoss = StopLoss(open_price=self.open,
                                               high_price=self.high,
                                               low_price=self.low,
                                               close_price=self.close,
                                               open_datetime=self.open_datetime,
                                               trade_side=self.trade_side,
                                               pip_decimal_position=self.pip_decimal_position,
                                               stop_loss_width=self.stop_loss_pips,
                                               )
        stop_loss: Barrier = stop_loss_barrier.compute()
        self.multi_barrier.barriers.append(stop_loss)

    def compute_time_barrier(self):
        time_barrier: TimeBarrier = TimeBarrier(close_price=self.close,
                                                time_barrier_periods=self.time_barrier_periods,
                                                open_datetime=self.open_datetime
                                                )
        time_barrier: Barrier = time_barrier.compute()
        self.multi_barrier.barriers.append(time_barrier)

    def compute_dynamic_barrier(self):
        dynamic_barrier: DynamicBarrier = DynamicBarrier(open_price=self.open,
                                                         exit_signals=self.dynamic_exit,
                                                         open_datetime=self.open_datetime
                                                         )
        dynamic_barrier: Barrier = dynamic_barrier.compute()
        self.multi_barrier.barriers.append(dynamic_barrier)

    def select_first_hit(self):
        first_hit: Barrier | None = None
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
        self._pip_factor: float = 10 ** (-pip_decimal_position)
        self._pip_decimal_position: int = pip_decimal_position

        if take_profit_width is not None:
            self._take_profit_decimal: float = take_profit_width * self._pip_factor
        self._take_profit_level = take_profit_level

        self.barrier: Barrier = Barrier(barrier_type=BarrierType.TAKE_PROFIT)

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

        self.barrier: Barrier = Barrier(barrier_type=BarrierType.STOP_LOSS)

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

        self.barrier = Barrier(barrier_type=BarrierType.TIME_BARRIER)

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

        self.barrier: Barrier = Barrier(barrier_type=BarrierType.DYNAMIC)

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
