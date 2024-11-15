import abc

import pandas as pd
from abc import ABC


class Strategy(ABC):

    def __init__(self, pip_position: int):
        self.pip_position: int = pip_position
        self.pip_factor = 1/10**pip_position

    @staticmethod
    def calculate_features(price: pd.DataFrame, fast_perioids: int, slow_periods: int):
        price[f"mva-{fast_perioids}"] = price["close"].rolling(fast_perioids).mean().round(5)
        price[f"mva-{slow_periods}"] = price["close"].rolling(slow_periods).mean().round(5)
        price.dropna(inplace=True)

    @abc.abstractmethod
    def calculate(self, price: pd.DataFrame, fast_periods: int, slow_periods: int):
        pass


class LongStrategy(Strategy):

    def __init__(self, pip_position):
        super().__init__(pip_position)

    def calculate(self, price: pd.DataFrame, fast_periods: int, slow_periods: int):
        """

        fast_mva_i-1 below slow_mva_i-1
        fast_mva_i above slow_mva_i ^      : fast mva crossing above slow mva
        close_price_i > open_price_i      : last closed bar long


        :param price:
        :param output_col_name:
        :return:
        """

        self.calculate_features(price, fast_periods, slow_periods)

        mask_signal = (price[f"mva-{fast_periods}"].shift(1) <= price[f"mva-{slow_periods}"].shift(1)) & \
                      (price[f"mva-{fast_periods}"] > price[f"mva-{slow_periods}"]) & \
                      (price["close"] > price["open"])
        price.loc[mask_signal, "long-signal"] = 1
        price["long-entry"] = price["long-signal"].shift(1)

        price.loc[mask_signal, "long-signal-plot"] = price[mask_signal]["low"] - 5*self.pip_factor
        mask_entry = price["long-entry"] == 1
        price.loc[mask_entry, "long-entry-plot"] = price[mask_entry]["low"] - 5*self.pip_factor

        return price


class ShortStrategy(Strategy):  

    def __init__(self, pip_position):
        super().__init__(pip_position)


    def calculate(self, price: pd.DataFrame, fast_periods: int, slow_periods: int) -> pd.DataFrame:
        """
        fast_mva_i-1 above slow_mva_i-1
        fast_mva_i below slow_mva_i ^      : fast mva crossing below slow mva
        close_price_i < open_price_i      : lost last closed bar short

        :param price:
        :param output_col_name:
        :return:
        """

        self.calculate_features(price, fast_periods, slow_periods)

        mask_signal = (price[f"mva-{fast_periods}"].shift(1) >= price[f"mva-{slow_periods}"].shift(1)) & \
                      (price[f"mva-{fast_periods}"] < price[f"mva-{slow_periods}"]) & \
                      (price["close"] < price["open"])
        price.loc[mask_signal, "short-signal"] = 1
        price["short-entry"] = price["short-signal"].shift(1)

        price.loc[mask_signal, "short-signal-plot"] = price[mask_signal]["high"] + 5*self.pip_factor
        mask_entry = price["short-entry"] == 1
        price.loc[mask_entry, "short-entry-plot"] = price[mask_entry]["high"] + 5*self.pip_factor

        return price
