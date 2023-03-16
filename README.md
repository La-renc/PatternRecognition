# PatternRecognition
![patternrecognitioncover](https://user-images.githubusercontent.com/125923909/225727628-e5d348c4-fb09-4426-a921-c10732e52ebb.png)

## Summary
In this project we will develop a program to search for some common known candlestick pattern in stock charts and classify them according to their shapes. We will also try to define how strong the patterns are and does it really has a subsequence effect on the future price.
## Background
In stock market trading, it is commonly believed that a certain candlestick patterns are a sign of the future price trend. We will focus on the following patterns:
1. Engulfing candlestick
2. Doji (under construction)
## How is it used?
An engulfing candlestick is defined as:
- The length of the current candle is longer than its previous candle
- The range of previous open to close prices is within the range of current open to close prices
- The direction of the candles are in opposite direction

We will also define the apparent strength of the candle as the difference of the open and close price ranges of previous and current candles divided by the open and close price ranges of the current candle. We define it this way so that the value of strength is between 0 and 1.
Let's take a bullish candlestick as an example:
