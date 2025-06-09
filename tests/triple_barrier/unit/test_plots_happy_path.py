from datetime import datetime
from triple_barrier import constants
from triple_barrier.plots import PlotTripleBarrier


class TestPlots:

    def test_build_ohlc(self, prepare_price_data):
        df = prepare_price_data
        plotter = PlotTripleBarrier(
            df[constants.OPEN],
            df[constants.HIGH],
            df[constants.LOW],
            df[constants.CLOSE],
            pip_decimal_position=4,
            periods_after=5,
            periods_before=5,
        )

        ohlc = plotter.build_ohlc(
            df[constants.OPEN],
            df[constants.HIGH],
            df[constants.LOW],
            df[constants.CLOSE],
        )

        assert (ohlc[constants.OPEN] - df[constants.OPEN]).sum() == 0
        assert (ohlc[constants.HIGH] - df[constants.HIGH]).sum() == 0
        assert (ohlc[constants.LOW] - df[constants.LOW]).sum() == 0
        assert (ohlc[constants.CLOSE] - df[constants.CLOSE]).sum() == 0

    def test_calculate_plotting_range_extension_full_range(self, prepare_price_data):
        df = prepare_price_data

        plotter = PlotTripleBarrier(
            df[constants.OPEN],
            df[constants.HIGH],
            df[constants.LOW],
            df[constants.CLOSE],
            pip_decimal_position=4,
        )

        date_from = "2023-01-02 02:00:00"
        date_to = "2023-01-02 03:00:00"

        date_from_extended, date_to_extended = (
            plotter._calculate_plotting_range_extension(date_from, date_to)
        )

        assert date_from_extended == datetime.strptime(
            "2023-01-02 01:35:00", "%Y-%m-%d %H:%M:%S"
        )
        assert date_to_extended == datetime.strptime(
            "2023-01-02 03:25:00", "%Y-%m-%d %H:%M:%S"
        )

        # How to covert a string to a datetime object
