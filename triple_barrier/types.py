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

    def __str__(self):
        output_str: str = f"""
        \nFirst Hit: \n
        Hit type {self.first_hit.order_type.value}
        Hit datetime {self.first_hit.hit_datetime}
        "Hit price {self.first_hit.level}
        """

        barrier_hits: list = [str(hit) for hit in self.barriers]

        return output_str + "\nOther hits \n" + "\n".join(barrier_hits)
