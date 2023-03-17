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

The following code finds out in which time slot the bullish and bearish engulfing candles occurs:
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
def draw_candles(df=pd.DataFrame):
    fig = plt.figure(figsize=(18,9))
    ax_ohlc = fig.add_subplot(9,1,(1,7))
    ax_vol = fig.add_subplot(9,1,9,sharex=ax_ohlc)
    fig.suptitle('Engulfing candlesticks', fontsize=16)
    dates = [idx.strftime('%Y-%m-%d') for idx in df.index]
    locs = []
    for i in range(1,len(df.index)):
        if df.index[i-1].month != df.index[i].month:
            locs.append(i)
    candle_colors=[]
    for j in df['close']-df['open']:
        if j>0: candle_colors.append('green')
        elif j==0: candle_colors.append('black')
        else: candle_colors.append('red')
    ax_ohlc.bar(dates, df['high']-df['low'], bottom=df['low'], width=0.3, color='black')
    ax_ohlc.bar(dates, df['close']-df['open'], bottom=df['open'], width=0.9, color=candle_colors)
    list_bull_eng=[idx.strftime('%Y-%m-%d') for idx in df.index[df['bullish_engulf']]]
    ax_ohlc.scatter(list_bull_eng, 0.98*df['low'][df['bullish_engulf']], label='bullish_engulf', color='g', marker='^')
    list_bear_eng=[idx.strftime('%Y-%m-%d') for idx in df.index[df['bearish_engulf']]]
    ax_ohlc.scatter(list_bear_eng, 0.98*df['low'][df['bearish_engulf']], label='bearish_engulf', color='r', marker='v')
    
    ax_ohlc.xaxis.set_major_locator(mticker.FixedLocator(locs, nbins=None))
    ax_ohlc.set_ylim(bottom=0.97*df['low'].min(), top=1.03*df['high'].max())
    ax_ohlc.yaxis.set_ticks_position(position='right')
    ax_ohlc.grid(visible=True)#, which='major')
    ax_ohlc.legend()
    ax_vol.bar(dates, df['volume'], width=0.9, color=candle_colors)
    ax_vol.grid(visible=True)#, which='major')
    plt.setp(ax_ohlc.get_xticklabels(), rotation=45)
    plt.setp(ax_vol.get_xticklabels(), rotation=45)
    plt.show()
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


