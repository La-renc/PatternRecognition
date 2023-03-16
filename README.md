# PatternRecognition
![patternrecognitioncover](https://user-images.githubusercontent.com/125923909/225727628-e5d348c4-fb09-4426-a921-c10732e52ebb.png)

## Summary
In this project we will develop a program to search for some common known candlestick pattern in stock charts and classify them according to their shapes. We will also try to define how strong the patterns are and does it really has a subsequence effect on the future price.
## Background
In stock market trading, it is commonly believed that a certain candlestick patterns are a sign of the future price trend. We will focus on the following patterns:
1. Engulfing candlestick
2. Doji (under construction)
## Engulfing candlestick
An engulfing candlestick is defined as:
- The length of the current candle is longer than its previous candle
- The range of previous open to close prices is within the range of current open to close prices
- The direction of the candles are in opposite direction

We will also define the "engulfing percentage" of the candle as the length difference of the current and previous candles divided by the length of current candle. We define it this way so that the value is between 0 and 1. It is believed that the more bullish engulfing the candles are, the price will tend to go up more.
Let's take a look at a bullish candlestick as an example:

![patternrecognitionbullish](https://user-images.githubusercontent.com/125923909/225757432-f4a784df-2c01-4f5d-9348-15f0d71cf404.png)

engulfing percentage = (current length - previous length) / current length

For bearish engulf pattern the opposite happens.

As an example, let's take the daily candle chart of MSFT in 2022 and run the code:
![patternrecognitioncandles](https://user-images.githubusercontent.com/125923909/225765999-9b3370c6-59ec-4f30-bbd8-77a1db6d0fbb.png)
The bullish and bearish engulf candles are marked with green and red triangle respectively.

We would like to find out the correlation of the engulf candles with future price trend. As an price trend indicator, let's take the mean of daily close prices following an engulfing candle, and find its percentage difference compare to the current close price. We will start with 14 future days.
