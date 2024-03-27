# WARNING:

This is a work in progress DO NOT USE IT FOR PRODUCTION PURPOSES

# Overview

Triple Barrier is a trade labeler that con be used in the context of back-testing or machine learning trading and
validating process. It records for each trade when, at what price level and why a trade was closed.

![](./docs/images/trades-table.png)

Includes features to plot the triple for a particular trade and the closing event:

![](./docs/images/trade_example_1.png)

Other features:

- Built
  upon [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), [mplfinance](https://github.com/matplotlib/mplfinance).
- Works semi vectorized, meaning that can be used with a pandas apply function.

## Why?

This project emerges from repeated trading strategy back-testing process where I was caught again and again copying and
pasting from previous pipelines the code to perform a vectorized (semi-vectorized to be more accurate) labeling of
trades. To avoid this DRY routine is that I decide to move this code to a library.

The name and core idea is inspired in an algorithm found in the book: Advances in Financial Machine Learning, by Marcos
Lopez de Prado.

Before going moving further into library details a little bit of context.

### Trading Strategies

A trading strategy describes the logic for opening trades, managing and closing positions.

Depending on the trading strategy, after a position is opened, four events will determine how the position ends:

1. Stop loss hit: The price hit the stop loss, which is the maximum tolerable loss (Limit Order)
2. Take profit hit: The price hit the take profit, which is the estimated maximum profit the position can reach (Limit
   Order)
3. Expiration time reached: The position has reached a specific expiration time (Good Til Time or GTT orders)
4. A custom condition: Any custom condition that can maximize the position profit. These conditions depend on price
   action whuile the position is opened

![](./docs/images/triple-barrier-long.png)

To determine if strategy is potentially profitable before live trading, it is necessary to collect a large sample of
trades to
analyze the effectiveness of the strategy in terms of profits, mean profits, profits distributions, draw-downs or any
metric you prefer.

Doing this analysis process manually is not recommended at all, considering the amount of data you need to analyze, the
volume of trades required to determine if the strategy is significantly profitable and the human error, to name a few
reasons. Suppose you have
ten trading strategy models, each one with ten permutations of parameter values (this can lead to over-fitting, I know)
and
suppose you want to collect samples over ten years at a frequency (time-frame) of 5 minutes, impossible, isn't it?

## Enter Algorithmic Trading

In simple terms, through algorithmic trading is using software to automate all the process described above: Open, manage
and Close trading positions.

But before running live a trading algorithm that implements a trading model you need to perform some research and
analyze the algorithm behavior on historic data to understand whether the algorithm is able to generalize and
potentially behave similarly on unseen or future data, this process is called back-testing.

Is in back-testing where you need to identify: when positions where opened, when and why they were closed.

## Enter Triple Barrier

So Triple Barrier automates the recording of trades in the context of back-testing or machine learning as well
to label trade profit/loss, closing event or any other value you can calculate from the data provided by triple barrier.

## How?

For now please refer to the tests to understand how triple barrier works:

[Triple barrier test](./tests/triple_barrier/integration/test_triple_barrier_apply_happy_path.py)

Or to this Jupyter Notebook that combines triple barrier calculation with plotting.

[Triple Barrier Jupyter Notebook](./docs/plot-method-tests.ipynb)

In the future extensive amount of examples will be used.

### How to install

As of now, the latest version (Release candidate) is 0.4.1rc and can be installed as follows:

```commandline
pip install triple-barrier==0.4.2rc0
```

# References

[Why numpy is fast](https://numpy.org/doc/stable/user/whatisnumpy.html#why-is-numpy-fast)
