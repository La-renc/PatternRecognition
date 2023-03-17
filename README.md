# PatternRecognition
![patternrecognitioncover](https://user-images.githubusercontent.com/125923909/225727628-e5d348c4-fb09-4426-a921-c10732e52ebb.png)

## Summary
In this project we will develop a program to search for some common known candlestick pattern in stock charts and classify them according to their shapes. We will also try to define how strong the patterns are and does it really has a subsequence effect on the future price.
## Background
In stock market trading, it is commonly believed that a certain candlestick patterns are a sign of the future price trend. We will focus on the following patterns:
1. Engulfing candlestick
2. Doji (under construction)
## Engulfing candlestick
As an example, let's take the daily candle chart of MSFT in 2022 and find the engulfing candles in the chart.
```
#----Download candlestick data of MSFT-----------------------------------------
df = pd.read_csv('MSFT_ohlcv.csv', index_col=0, parse_dates=True)
df.index = [d.date() for d in df.index]
```

An engulfing candlestick is defined as:
- The length of the current candle is longer than its previous candle
- The range of previous open to close prices is within the range of current open to close prices
- The direction of the candles are in opposite direction

An example of bullish engulfing candlestick as follows:

![patternrecognitionbullish](https://user-images.githubusercontent.com/125923909/225757432-f4a784df-2c01-4f5d-9348-15f0d71cf404.png)

The following code finds in which time slot the bullish and bearish engulfing candles occurs:
```
#----Setup conditions to distinguish bullish and bearish engulfing candlesticks
df['c_t-1'] = df['close'].shift(1)
df['o_t-1'] = df['open'].shift(1)
df['c-o'] = df['close']-df['open']
df['bull_candle'] = df['c-o']>0
df['bear_candle'] = df['c-o']<0
df['bull_candle_t-1'] = df['bull_candle'].shift(1)
df['bear_candle_t-1'] = df['bear_candle'].shift(1)
df['c>co_t-1'] = df['close']>df[['c_t-1','o_t-1']].max(axis=1)
df['c<co_t-1'] = df['close']<df[['c_t-1','o_t-1']].min(axis=1)
df['o>co_t-1'] = df['open']>df[['c_t-1','o_t-1']].max(axis=1)
df['o<co_t-1'] = df['open']<df[['c_t-1','o_t-1']].min(axis=1)

#----Identify whether the current time slot has engulfing candlesticks---------
df['bullish_engulf'] = df[['bear_candle_t-1','bull_candle','c>co_t-1','o<co_t-1']].all(axis=1)
df['bearish_engulf'] = df[['bull_candle_t-1','bear_candle','c<co_t-1','o>co_t-1']].all(axis=1)
```

Display the candlestick chart with the function draw_candles.
```
draw_candles(df)
```

The bullish and bearish engulf candles are marked with green and red triangle respectively.
![patternrecognitioncandles](https://user-images.githubusercontent.com/125923909/225765999-9b3370c6-59ec-4f30-bbd8-77a1db6d0fbb.png)


We will also define the "engulfing percentage" of the candle as the length difference of the current and previous candles divided by the length of current candle. We define it this way so that the value is between 0 and 1. It is believed that the more bullish engulfing the candles are, the price will tend to go up more, and the opposite would happen for bearish engulfing candles.
The following code calculates the engulfing percentage:
```
#----Setup parameters to measure how bullish/bearish the engulfing candlesticks appear to be
mask = df[['bullish_engulf','bearish_engulf']].any(axis=1)
df['candle_len'] = abs(df['c-o'])
df['candle_len_t-1'] = df['candle_len'].shift(1)
df['engulf_pct'] = 1 - df['candle_len_t-1'][mask]/df['candle_len'][mask]
```

We would like to find out the correlation of the engulf candles with future price trend. As an price trend indicator, let's take the mean of daily close prices following an engulfing candle, and find its percentage difference compare to the current close price: The following code calculates the future trend, we will start with 14 future days' prices.
```
#----Setup the mean price of the future candlesticks to define future trend----
future_window = 14
df['mean_next'+str(future_window)] = df['close'].rolling(future_window).mean().shift(-future_window)
df['trend'] = df['mean_next'+str(future_window)]/df['close'] - 1
```
If the mean future prices is higher than the current close price, the trend is positive, and vice versa.

Next we see if there is any correlation between the occurence of engulfing candles and future price trend. We do so by plotting correlation graph using function draw_corr:
```
draw_corr(df, 'engulf_pct', 'trend')
```
![patternrecognitioncorr](https://user-images.githubusercontent.com/125923909/225984338-c275a1e8-0903-4049-9786-caf0b6e806d4.png)
The result shows that the correlation between the engulfing candles and future mean price is quite low, only 0.2337 and -0.3360. Especially for the bullish gulfing candles, even they occured, the future mean prices are mostly below the current close prices.

Next, let's grid search a few different lengths of future days and see what would happen.

| Days     | Bull Corr | Bear Corr |
|----------|-----------|-----------|
|3         |     0.5334|    -0.2961|
|4         |     0.5198|    -0.3632|
|5         |     0.4890|    -0.2978|
|6         |     0.4657|    -0.3088|
|7         |     0.4596|    -0.2817|
|8         |     0.4501|    -0.3131|
|9         |     0.4060|    -0.3353|
|10        |     0.3404|    -0.3231|
|11        |     0.3052|    -0.3315|
|12        |     0.2688|    -0.3264|
|13        |     0.2467|    -0.3430|
|14        |     0.2337|    -0.3360|

From the result, the correlation of bullish engulf candles are better as the days get shorter, which means that it works better in shorter term. For bearish engulf candles it gets slightly worse in shorter term. It seems the sweet spot is around 9 days. In all the length of days, the bullish shows a positive correlation to future trend and bearish shows negative, which is as we would expected them to be. However the correlation values are quite low (mostly around 0.3)

It is also believed that if the volume of the candle is greater, the bullishness or bearishness is also greater. Let's define volume change by comparing the current volume with previous volume. If current volume is greater than previous then the value is >1, and vice versa. Then multiply it with the engulf percentage.

```
#----Setup parameters to measure how bullish/bearish the engulfing candlesticks appear to be
mask = df[['bullish_engulf','bearish_engulf']].any(axis=1)
df['candle_len'] = abs(df['c-o'])
df['candle_len_t-1'] = df['candle_len'].shift(1)
df['engulf_pct'] = 1 - df['candle_len_t-1'][mask]/df['candle_len'][mask]
df['v_pct'] = df['volume']/df['volume'].shift(1)
df['engulfxvol'] = df['engulf_pct'][mask]*df['v_pct'][mask]
```

Grid search again with feature changed to 'engulfxvol'.
```
draw_corr(df, 'engulfxvol', 'trend')
```

| Days     | Bull Corr | Bear Corr |
|----------|-----------|-----------|
|3         |     0.3671|    -0.6610|
|4         |     0.4063|    -0.7514|
|5         |     0.3845|    -0.7386|
|6         |     0.3759|    -0.7281|
|7         |     0.3623|    -0.7061|
|8         |     0.3343|    -0.7253|
|9         |     0.2918|    -0.7182|
|10        |     0.2266|    -0.6822|
|11        |     0.1863|    -0.6661|
|12        |     0.1463|    -0.6485|
|13        |     0.1344|    -0.6499|
|14        |     0.1424|    -0.6436|

The result shows that the bearish engulfing candle correlates much better after multiplying the volume change. However the correlation on the bullish side got worse. This would suggested that the overall trend of the stock during this period of time is bearish (as we can see on the candlestick chart).
The result also shows that both correlations get better as the length of future days are shorter, suggesting that it has a very short term effect.

From the experiment above, we can see that an occurence of an engulfing candlestick alone is not a good indication of future price trend. It might be useful when using it together with some other technical indicators for price trend prediction.





