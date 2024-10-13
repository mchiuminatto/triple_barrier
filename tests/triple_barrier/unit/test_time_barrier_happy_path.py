from datetime import datetime, timedelta

import numpy as np
from dateutil import parser
from triple_barrier import constants as const

from triple_barrier.trade_labeling import (
    TimeBarrier
)


class TestTimeBarrier:

    def test_time_barrier_hit(self, prepare_price_data):
        df = prepare_price_data
        trade_open_datetime: datetime = parser.parse("2023-01-02 20:45:00")
        time_barrier_periods: int = 10
        time_limit_date: datetime = df[trade_open_datetime:].index[time_barrier_periods]

        time_barrier = TimeBarrier(open_price=df.open,
                                   time_limit_date=time_limit_date,
                                   open_datetime=trade_open_datetime)
        time_barrier.compute()

        assert time_barrier.barrier.hit_datetime == parser.parse("2023-01-02 21:35:00")
        assert time_barrier.barrier.level == df.loc["2023-01-02 21:35:00":]["open"].iloc[0]

    def test_time_barrier_hit_beyond_limit(self, prepare_price_data):
        df = prepare_price_data
        trade_open_datetime: datetime = parser.parse("2024-02-02 17:25:00")
        time_barrier_periods: int = 20
        time_limit_date: datetime = datetime.now() + timedelta(days=time_barrier_periods)


        time_barrier = TimeBarrier(open_price=df.open,
                                   time_limit_date=time_limit_date,
                                   open_datetime=trade_open_datetime)
        time_barrier.compute()

        assert time_barrier.barrier.hit_datetime == const.INFINITE_DATE
        assert time_barrier.barrier.level == np.Inf
