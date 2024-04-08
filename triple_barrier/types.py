from enum import Enum
from datetime import datetime


class OrderType(Enum):
    TAKE_PROFIT = "take-profit"
    STOP_LOSS = "stop-loss"
    TIME_EXPIRATION = "time-expiration"
    DYNAMIC = "dynamic"


class ExitType(Enum):
    TAKE_PROFIT_HIT = "take-profit-hit"
    STOP_LOSS_HIT = "stop-loss-hit"
    TIME_BARRIER_HIT = "tme-barrier-hit"
    DYNAMIC_BARRIER_HIT = "dynamic-barrier-hit"


class TradeSide(Enum):
    BUY = 1
    SELL = -1


class OrderHit:

    def __init__(self,
                 level: float | None = None,
                 hit_datetime: datetime | None = None,
                 order_type: OrderType | None = None
                 ):
        self.level: float = level
        self.hit_datetime: datetime = hit_datetime
        self.order_type: OrderType = order_type

    def __str__(self):
        output: str = f"""
        Datetime: {self.hit_datetime}
        Level: {self.level}
        Type: {self.order_type.value}
        """
        return output


class OrderBoxHits:
    def __init__(self) -> None:
        self.barriers: list[OrderHit] = []
        self.first_hit: OrderHit = OrderHit()

    # TODO: Implement a good string representation
