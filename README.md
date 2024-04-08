# WARNING:

This is a work in progress DO NOT USE IT FOR PRODUCTION PURPOSES

# Overview

Triple Barrier is a trade labeler that can be used for algorithmic trading back-testing or machine learning training and
validating pipelines. It records for each trade when, at what price level and why a position was closed.

![](./docs/images/trades-table.png)

It includes features to plot the triple for a particular trade and the closing event:

![](./docs/images/trade_example_1.png)

Other features:

- Built
  upon [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), [matplotlib](https://matplotlib.org/) [mplfinance](https://github.com/matplotlib/mplfinance).
- It can be used to label single trades or semi vectorized, meaning that can be used with a pandas apply function.

## Why?

This project emerges from a repeated trading strategy back-testing process where I was caught again and again copying 
and pasting from previous pipelines the code to perform a vectorized (semi-vectorized to be more accurate) labeling of 
trades. To avoid this DRY (Do not Repeat Yourself) routine, that is why I decided to move this code to a library.

The name and core idea were inspired by an algorithm found in the book: Advances in Financial Machine Learning, by Marcos
Lopez de Prado.

Before moving further into the library details a little bit of context.

### Trading Strategies

A trading strategy describes the logic for opening, managing and closing positions.

Depending on the trading strategy, once a position is opened, four events can determine how the position ends:

1. Stop loss hit: The price hit the stop loss, which is the maximum tolerable loss (Limit Order)
2. Take profit hit: The price hit the take profit, which is the estimated maximum profit the position can reach (Limit
   Order)
3. Expiration time reached: The position has reached a specific expiration time (Good Til Time or GTT orders)
4. A custom condition: Any custom condition that can trigger the position closing. These conditions depend on price
   action while the position is opened

![](./docs/images/triple-barrier-long.png)

To determine if a strategy is potentially profitable before live trading, it is necessary to collect a large sample of
trades to analyze the effectiveness of the strategy in terms of profits, mean profits, profits distributions, drawdowns
or any metric you prefer.

Doing this analysis process manually is not recommended at all, considering the amount of data you need to analyze, the
volume of trades required to determine if the strategy is significantly profitable and the human error, to name a few
reasons. 

## Algorithmic Trading and Triple Barrier

In simple terms, algorithmic trading is using software to automate all the processes described above: Open, manage
and Close trading positions.

But before running live a trading algorithm that implements a trading model you need to perform some research and
analyze the algorithm behavior on historic data to understand whether the algorithm is able to generalize well and
 behave similarly on unseen or future data, this process is called back-testing.

Is in back-testing where you need to identify: when positions were opened, when and why they were closed, so you can 
calculate all required performance metrics and that is why Triple Barrier was built for.


## How?

### How to install

```commandline
pip install triple-barrier==0.4.3rc0
```


[Triple barrier test](./tests/triple_barrier/integration/test_triple_barrier_apply_happy_path.py)

Or to this Jupyter Notebook that combines triple barrier calculation with plotting.

[Triple Barrier Jupyter Notebook](./docs/plot-method-tests.ipynb)


### How to install

As of now, the latest version (Release candidate) is 0.4.1rc and can be installed as follows:

```commandline
pip install triple-barrier==0.4.2rc0
```

### Examples

This is a work in progress, but you can find some examples here:

You can see use case examples in this [folder](./docs/examples)

## TODO

This project is its final stages of testing, documentation and CLEANing.

Besides that, there are some identified tasks that need to be done before the first release.

- Add string representations for some classes
- Provide an out-of-the-box function that can be easily used by pandas apply . Currently, you need to build one.
- Refactor list of barriers hits (OrderBoxHits.barriers) as dictionary, currently is a list which
is not much actionable.
- Plotting: Add possibility to plot oscillators in a panel below
- Add trailing stops


## Other Documentation

[Uml models](./docs/models.md)

# References

[Why numpy is fast](https://numpy.org/doc/stable/user/whatisnumpy.html#why-is-numpy-fast)
