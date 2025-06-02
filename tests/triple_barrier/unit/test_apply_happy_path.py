
import pandas as pd

from triple_barrier.trading import DataSetLabeler
from triple_barrier.trade_labeling import TradeSide
from triple_barrier.trading import TradingParameters
import triple_barrier.constants as const

from PIL import Image

OUTPUT_FOLDER: str = f"{const.ROOT_FOLDER}/tests/triple_barrier/integration/output/"
TAKE_PROFIT_WIDTH = 10
STOP_LOSS_WIDTH = 5
PIP_DECIMAL_POSITION = 4
TIME_BARRIER_PERIODS = 10


class TestTripleBarrierApply:
    """
    This set, tests the class and method that makes abstraction of
    apply execution on a pandas dataset,
    """

    def test_long(self,
                  prepare_price_data):

        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.BUY,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)
        trades: pd.DataFrame = dataset_labeler.compute()

        trades.to_parquet(f"{OUTPUT_FOLDER}/test-apply-long-no-dynamic-exit.parquet")

        for row in trades.iterrows():
            if row[1]["close-type"] == "time-expiration":
                assert row[1]["profit"] != 40 and row[1]["profit"] != 20
            elif row[1]["close-type"] == "stop-loss":
                assert row[1]["profit"] == -20.00
            else:
                assert row[1]["profit"] == 40.00

    def test_short(self,
                   prepare_price_data):

        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=20,
            take_profit_width=40,
            trade_side=TradeSide.SELL,
            pip_decimal_position=4,
            time_barrier_periods=10,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)

        trades: pd.DataFrame = dataset_labeler.compute()

        trades.to_parquet(f"{OUTPUT_FOLDER}/test-apply-short-no-dynamic-exit.parquet")

        for row in trades.iterrows():
            if row[1]["close-type"] == "time-expiration":
                assert row[1]["profit"] != 40 and row[1]["profit"] != 20
            elif row[1]["close-type"] == "stop-loss":
                assert row[1]["profit"] == -20.00
            else:
                assert row[1]["profit"] == 40.00



    def test_long_plot(self,
                   prepare_price_data):
        
        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=STOP_LOSS_WIDTH,
            take_profit_width=TAKE_PROFIT_WIDTH,
            trade_side=TradeSide.BUY,
            pip_decimal_position=PIP_DECIMAL_POSITION,
            time_barrier_periods=TIME_BARRIER_PERIODS,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)

        trades: pd.DataFrame = dataset_labeler.compute()
        
        dataset_labeler.plot(trade_date=trades.index[0],
                                     overlay_features=[df["mva-12"], df["mva-24"]],
                                     oscillator_features=[df["awo"]],
                                     save_plot=True,
                                     plot_folder=OUTPUT_FOLDER)
        
        try:
            reference_image = Image.open(f"{OUTPUT_FOLDER}/long_reference.png")
        except FileNotFoundError:
            reference_image = None
            
        try:
            produced_image = Image.open(f"{OUTPUT_FOLDER}/triple_barrier_2023-01-02 08_05_00.png")
        except FileNotFoundError:
            reference_image = None
        
        assert reference_image.size == produced_image.size
  
            
        
    def test_short_plot(self,
                prepare_price_data):
    
        df = prepare_price_data

        trade_params = TradingParameters(
            open_price=df.open,
            high_price=df.high,
            low_price=df.low,
            close_price=df.close,
            entry_mark=df.entry,
            stop_loss_width=STOP_LOSS_WIDTH,
            take_profit_width=TAKE_PROFIT_WIDTH,
            trade_side=TradeSide.SELL,
            pip_decimal_position=PIP_DECIMAL_POSITION,
            time_barrier_periods=TIME_BARRIER_PERIODS,
            dynamic_exit=None
        )

        dataset_labeler = DataSetLabeler(trade_params)

        trades: pd.DataFrame = dataset_labeler.compute()
        
        dataset_labeler.plot(trade_date=trades.index[1],
                                     overlay_features=[df["mva-12"], df["mva-24"]],
                                     oscillator_features=[df["awo"]],
                                     save_plot=True,
                                     plot_folder=OUTPUT_FOLDER)
         
        try:
            reference_image = Image.open(f"{OUTPUT_FOLDER}/short_reference.png")
        except FileNotFoundError:
            reference_image = None
            
        try:
            produced_image = Image.open(f"{OUTPUT_FOLDER}/triple_barrier_2023-01-02 20_45_00.png")
        except FileNotFoundError:
            reference_image = None
        
        assert reference_image.size == produced_image.size
  
