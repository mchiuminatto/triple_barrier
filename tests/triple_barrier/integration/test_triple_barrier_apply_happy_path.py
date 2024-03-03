
import pandas as pd
from triple_barrier.triple_barrier import (TradeSide,
                                           MultiBarrierBuilder
                                           )


class TestTripleBarrierApplyCases:
    def test_use_in_pandas_apply(self, prepare_price_data):
        df = prepare_price_data

        def calculate_exit(row: any,
                           ohlc: pd.DataFrame,
                           stop_loss_width: float,
                           take_profit_width: float,
                           trade_side: TradeSide,
                           pip_decimal_position: int,
                           time_barrier_periods: int):
            barrier_builder = MultiBarrierBuilder(open_price=ohlc.open,
                                                  high_price=ohlc.high,
                                                  low_price=ohlc.low,
                                                  close_price=ohlc.close,
                                                  trade_open_datetime=str(row.name),
                                                  stop_loss_pips=stop_loss_width,
                                                  take_profit_pips=take_profit_width,
                                                  trade_side=trade_side,
                                                  pip_decimal_position=pip_decimal_position,
                                                  time_barrier_periods=time_barrier_periods,
                                                  dynamic_exit=ohlc.exit)
            barrier_builder.compute()

            row["close-price"] = barrier_builder.multi_barrier.first_hit.level
            row["close-datetime"] = barrier_builder.multi_barrier.first_hit.hit_datetime
            row["close-type"] = barrier_builder.multi_barrier.first_hit.barrier_type.value

            return row

        entry = df[(df.entry == 1)]
        entry = entry.apply(calculate_exit, args=(entry, 5, 10, TradeSide.BUY, 4, 10), axis=1)



# TODO: Add more tests

# case 2.3 Take profit + Time barrier short, hit time barrier

# case 2.4 Stop loss + Time barrier long, hit stop loss
# case 2.5 Stop loss + Time barrier long, hit time barrier
# case 2.6 Stop loss + Time barrier short, hit stop loss
# case 2.7 Stop loss + Time barrier short, hit time barrier

# case 2.8 Take profit + Dynamic barrier long, hit take profit
# case 2.9 Take profit + Dynamic barrier long, hit Dynamic barrier
# case 2.10 Take profit + Dynamic barrier short, hit take profit
# case 2.11 Take profit + Dynamic barrier short, hit Dynamic barrier

# case 2.12 Stop loss + Dynamic barrier long, hit stop loss
# case 2.13 Stop loss + Dynamic barrier long, hit Dynamic barrier
# case 2.14 Stop loss + Dynamic barrier short, hit stop loss
# case 2.15 Stop loss + Dynamic barrier short, hit Dynamic barrier

# case set 3: Only time barrier

# case 3.1 time barrier long
# case 3.2 time barrier short

# case set 4: Only dynamic barrier
# case 4.1 dynamic barrier long
# case 4.2 dynamic barrier short
