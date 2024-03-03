import pytest
from triple_barrier.triple_barrier import (TradeSide,
                                           StopLoss,
                                           )


class TestTakeProfitError:

    def test_level_and_width(self, prepare_price_data, prepare_entry_data):
        df = prepare_price_data

        trade_open_datetime: str = "2023-01-02 20:45:00"

        with pytest.raises(ValueError) as error_instance:
            take_profit_barrier = StopLoss(open_price=df.open,
                                           high_price=df.high,
                                           low_price=df.low,
                                           close_price=df.close,
                                           open_datetime=trade_open_datetime,
                                           trade_side=TradeSide.BUY,
                                           pip_decimal_position=4,
                                           stop_loss_width=5,
                                           stop_loss_level=1.1300
                                           )
        assert "Either" in str(error_instance.value)
