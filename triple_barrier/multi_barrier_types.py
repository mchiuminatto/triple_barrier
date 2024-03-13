from enum import Enum
from datetime import datetime


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


class BarrierHit:

    def __init__(self,
                 level: float | None = None,
                 hit_datetime: datetime | None = None,
                 barrier_type: BarrierType | None = None
                 ):
        self.level: float = level
        self.hit_datetime: datetime = hit_datetime
        self.barrier_type: BarrierType = barrier_type

    def __str__(self):
        output: str = f"""
        Datetime: {self.hit_datetime} 
        Level: {self.level} 
        Type: {self.barrier_type.value}
        """
        return output


class MultiBarrierHit:
    def __init__(self) -> None:
        self.barriers: list[BarrierHit] = []
        self.first_hit: BarrierHit = BarrierHit()
