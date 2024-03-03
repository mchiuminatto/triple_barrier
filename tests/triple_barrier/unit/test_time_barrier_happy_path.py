from dateutil import parser
from triple_barrier.triple_barrier import (
                                           TimeBarrier,
                                           )


class TestTimeBarrier:

    def test_time_barrier_hit(self, prepare_price_data):
        trade_open_datetime: str = "2023-01-02 20:45:00"
        df = prepare_price_data
        time_barrier = TimeBarrier(close_price=df.close,
                                   time_barrier_periods=10,
                                   open_datetime=trade_open_datetime)
        time_barrier.compute()

        assert time_barrier.barrier.hit_datetime == parser.parse("2023-01-02 21:35:00")
        assert time_barrier.barrier.level == 1.06710
