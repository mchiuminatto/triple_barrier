from datetime import datetime
from dateutil import parser
from triple_barrier.trade_labeler import (
                                           DynamicBarrier,
                                           )


class TestDynamicBarrier:

    def test_dynamic_barrier_hit(self, prepare_price_data):
        trade_open_datetime: datetime = parser.parse("2023-01-03 21:25:00")
        df = prepare_price_data
        dynamic_barrier: DynamicBarrier = DynamicBarrier(
            open_price=df.open,
            exit_signals=df["exit-signal"],
            open_datetime=trade_open_datetime)
        dynamic_barrier.compute()

        assert dynamic_barrier.barrier.level == 1.05681
        assert dynamic_barrier.barrier.hit_datetime == parser.parse("2023-01-04 00:25:00")

