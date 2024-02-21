
# Overview

Please note that it is not the intend of this document to discuss the effectiveness of  different tools to estimate the potential profitability of a trading strategy. It is assumed that the audience of this document has some background in algorithmic trading and understand concepts like back-testing, machine learning labeling. 

## Why?

To support the vectorized testing or machine learning labeling and training of algorithmic trading strategies, making aware automation of when, at what price and why a trade was closed.

### Trading Strategies

A trading strategy describes the logic for opening, adjusting, closing, and controlling risk for a trading position. This actions are called position management in the rest of this document.

Depending on the trading strategy, after each position is opened four events determine when and at what price level the position is closed: The strategy hit the target (take profit hit), reached its maximum loss tolerance (take profit), reached the maximum time defined for the strategy (time expiry) or reached a strategy specific condition (dynamic close)

To determine if strategy is potentially profitable before live trading, it is necessary to collect a large sample to analyze the strategy in terms of profits, mean profits, profits distributions etc. It is out of the scope of this document to discuss trading strategy metrics.

Doing this manually nowadays is not recommendable, considering the technology available. 

Suppose the strategy is potentially profitable, but you have other ninety nine trading strategies to trade along, it is not possible to do it manually either.

The tools that solve this issues and lot more is algorithmic trading.

## Algorithmic Trading

In simple terms, algorithmic trading is using software to automate the position opening and management  in research time and production (live trading) time.

Research time is when you design, code test, collect data, make adjustments, demote or promote a strategy to live trading.

There are lot of tools you can use to test trading strategies, most of trading platforms offer scripting languages that allows you to code strategies, and back-test them and "optimize" them ( you should say over-fit them and yes this is opinionated).

Using a trading platform, though, will tie your strategies to brokers that support the platform you used.

## Python and Vectorization

Python and all its data science ecosystem (Pandas, Numpy, Scipy, Statslib, TA-lib, etc) allows you to be platform and broker agnostic, at least during the research stage so it is possible to code, test and/or train  your strategies on massive amounts of historic data so you can collect hundreds, thousands or millions of trades (positions) and get better estimations.

Running trading strategies over hundred of thousands or millions of records with core Python with loops, is intense resource consuming and slow. To overcome the slow part at least, is where vectorization comes handy.

There is one library the implements vectorization in python: Numpy. There is another relevant library the implement vectorization but in fact is built on top of Numpy.

Vectorization means that you can operate arrays and matrices like scalars, and behind the scenes Numpy implements the loops that solve all the operations. And yes loops again but the difference that Numpy is python interface to C routines that executes all the heavy duty task.


## What?
### Finally: Triple Barrier

In the time dimension, trades are defined between to event: open date time and close date time. In the price dimension are defined between open price and close price.

$(t_{open}, p_{open}), (t_{close}, p_{close})$

So for each trade recorded in a period of time you need to record those tuples.

Those values are set depending on which event is triggered first

1. Stop Loss: Price hit positions's stop loss level
2. Take Profit: Price hit positions's take profit level
3. Time Expiry: Price reached the time expiry
4. Dynamic condition: Price met a specified condition.

Triple barrier calculates all those events and the one that occurs first.

In essence, for each trade, triple barrier establishes a rectangle limited at the left by the open time, at the right either by the dynamic barrier or the time barrier. 

Depending on the trade side: BUY or SELL, the top and bottom barrier are set as follows:

For BUY positions, the top barrier is the take profit level and bottom barrier is the stop loss level. Conversely, if the trade side is  SELL, then the top barrier is the stop loss level and the bottom barrier is the take profit level.


## How?

### How to install

<todo>
### How to use

<todo>

### Examples

<todo>


# References

[Why numpy is fast](https://numpy.org/doc/stable/user/whatisnumpy.html#why-is-numpy-fast)
