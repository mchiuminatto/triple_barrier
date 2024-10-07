# Architecture Decision Record

## March 7th 2024

### Topic: plot barrier with triple barrier with the closing hit event

Regarding some question opened during the analysis of adding the plotting of the closing event to triple barrier, here are the decisions taken:

1. Will triple barriers implement trailing stops?

Not for now, but will be added to TODO list

2. Will dynamic barriers be plotted vertically or horizontally.

Considering that the only vertical barrier and in consequence the trade expiration time, and to be consequent with stop loss and take profit that are price levels and dynamic barrier either, dynamic barrier will be plotted horizontally

3. In the case there are more than one occurrence of a dynamic close event, before the time barrier, only the first one will be considered and plotted.

