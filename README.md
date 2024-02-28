# WARNING:

This is a work in progress

# Overview

Please note that it is not the intent of this document to discuss the effectiveness of  different tools to estimate the potential profitability of a trading strategy. It is assumed that the audience of this document has some background in algorithmic trading and understand concepts like back-testing, machine learning labeling.

## Why?

This project emerges from reapeted trading strategy back-testing process where I was caught again and again copying and pasting from previous pipelines the code to perform a vectorized (semi-vectorized to be more accurate) labeling of trades.

So this library performs the trade labeling in a semi-vectorized way and can be used from back-testing processes or machine learning training pipelines.

It is inspired ande named upon the algorithm presented in the book: Advances in Financial Machine Learning, by Marcos Lopez de Prado.

### Trading Strategies

A trading strategy describes the logic for opening, adjusting, closing, and controlling risk for a trading position. This actions are denoiminated as position management in the rest of this document.

Depending on the trading strategy, after each position is opened four events determine when and at what price level a position is closed: The strategy hit the target (hit on **take profit barrier**), reached its maximum loss tolerance (hit on **stop loss barrier**), reached the maximum time defined for the strategy (**hit on time limit barrier**) or reached a strategy specific condition (hit on **dynamic barrier**)

To determine if strategy is potentially profitable before live trading, it is necessary to collect a large sample to analyze the strategy in terms of profits, mean profits, profits distributions etc. It is out of the scope of this document to discuss trading strategy metrics.

Doing this manually nowadays is not recommendable at all, considering the technology available. Suppoose you have one hundred trading strategies, each with ten permutations of parameter values (yes that is called overfitting, I know and is not good, I know that either) and suppose you want to collect samples over ten years at a frequency (time-frame) of 5 minutes. Impossible.

## Algorithmic Trading

In simple terms, algorithmic trading is using software to automate the position opening and management  in research time and production (live trading) time.

Research time is when you design, code test, collect data, make adjustments, demote or promote a strategy to live trading.

There are lot of tools you can use to test trading strategies, most of trading platforms offer scripting languages that allows you to code strategies, and back-test them and "optimize" them (yes yes, overfitting)

Using a trading platform, though, will tie your strategies to brokers that support the platform you used and if you need to test a massive amount of algorithms, parameter variations over extended period of times, my experience says that a trading platform is not the best way.

## Python and Vectorization

Python and all its data science ecosystem (Pandas, Numpy, Scipy, Statslib, TA-lib, etc) allows you to be platform and broker agnostic, at least during the research stage so it is possible to code, test and/or train  your strategies on massive amounts of historic data sand collect hundreds, thousands or millions of trades (positions) to get better estimations.

Running trading strategies over hundred of thousands or millions of records with core Python with loops, is intense resource consuming and slow. To overcome the slow part, at least, is where vectorization comes handy.

There is one library that implements vectorization in python: Numpy. There is another relevant library the implement vectorization but in fact is built on top of Numpy: Pandas

Vectorization means that you can operate arrays and matrices like scalars, and behind the scenes Numpy implements the loops that solve all the operations, and yes loops again, but the difference is that Numpy is python interface to C routines that executes all the heavy duty tasks.

## What?

### Finally: Triple Barrier

In the time dimension, trades are defined between tow events: open date time and close date time. In the price dimension are defined between open price and close price. Expressed as tuples would be like so:

$(t_{open}, p_{open}), (t_{close}, p_{close})$

So for each trade recorded in a period of time you need to record those tuples.

Those values are set depending on which barrier or event is hit first: stop loss barrier, take profit barrier, time limit barrier or dynamic barrier.

Triple barrier calculates all those events and identifies the one that occurs first.

Depending on the trade side: BUY or SELL, the to price barrier could be either the stop loss barrier or the take profit barrier: For BUY positions, the top barrier is the take profit barrier and bottom one is the stop loss barrier. Conversely, if the trade side is  SELL, then the top barrier is the stop loss one and the bottom barrier is the take profit barrier.

## How?

### How to install

```shell
pip install triple-barrier
```


<todo>
### How to use

<todo>

<todo>

# References

[Why numpy is fast](https://numpy.org/doc/stable/user/whatisnumpy.html#why-is-numpy-fast)
