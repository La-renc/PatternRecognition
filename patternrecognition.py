import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

#----Functions-----------------------------------------------------------------
def draw_candles(df=pd.DataFrame):
    global future_window
    print('\nBullish engulf dates:')
    for idx in df.index[df['bullish_engulf']]: print(idx)
    print('\nBearlish engulf dates:')
    for idx in df.index[df['bearish_engulf']]: print(idx)

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
    ax_ohlc.bar([d.strftime('%Y-%m-%d') for d in df[df['close']-df['open']==0].index], [0.01 for _ in range(sum(df['close']-df['open']==0))], bottom=df['open'].loc[df['close']-df['open']==0], width=0.9, color=candle_colors)
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

def draw_corr(df=pd.DataFrame, featurex=str, featurey=str):
    global future_window
    
    bull = df['bullish_engulf']
    bear = df['bearish_engulf']
    corr_value_bull = df[[featurex, featurey]][bull].corr().iloc[0][1]
    corr_value_bear = df[[featurex,featurey]][bear].corr().iloc[0][1]
    print("\n| Days     | Bull Corr | Bear Corr |")
    print("|----------|-----------|-----------|")
    print(f"|{future_window:<10}|{corr_value_bull:>11,.4f}|{corr_value_bear:>11,.4f}|")

    fig = plt.figure(figsize=(10,4))
    ax0 = fig.add_subplot(1,10,(1,4))
    ax0.scatter(df[featurex][bull], df[featurey][bull])
    ax0.set(title=f"bullish_{featurex} vs {featurey}\ncorr={corr_value_bull:.4f}  Days={future_window}")
    ax0.set_xlabel(featurex)
    ax0.set_ylabel(featurey)
    ax1 = fig.add_subplot(1,10,(7,10), sharex=ax0, sharey=ax0)
    ax1.scatter(df[featurex][bear], df[featurey][bear])
    ax1.set(title=f"bearish_{featurex} vs {featurey}\ncorr={corr_value_bear:.4f}  Days={future_window}")
    ax1.set_xlabel(featurex)
    ax1.set_ylabel(featurey)
    plt.show()
    
def main():
    global future_window
    #----Download candlestick data of MSFT-----------------------------------------
    df = pd.read_csv('MSFT_ohlcv.csv', index_col=0, parse_dates=True)
    df.index = [d.date() for d in df.index]
    
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
    
    #----Setup parameters to measure how bullish/bearish the engulfing candlesticks appear to be
    mask = df[['bullish_engulf','bearish_engulf']].any(axis=1)
    df['candle_len'] = abs(df['c-o'])
    df['candle_len_t-1'] = df['candle_len'].shift(1)
    df['engulf_pct'] = 1 - df['candle_len_t-1'][mask]/df['candle_len'][mask]
    df['v_pct'] = df['volume']/df['volume'].shift(1)
    df['engulfxvol'] = df['engulf_pct'][mask]*df['v_pct'][mask]
    
    #----Setup the mean price of the future candlesticks to define future trend----
    # future_window = 14
    globals()['future_window'] = int(input("Enter the no. of time slots for future prices:"))
    df['mean_next'+str(future_window)] = df['close'].rolling(future_window).mean().shift(-future_window)
    df['trend'] = df['mean_next'+str(future_window)]/df['close'] - 1
    
    #------------------------------------------------------------------------------
    is_draw_candles = input("draw_candles? (y/n)")
    if is_draw_candles=='y': draw_candles(df)
    is_draw_corr = input("draw_corr? (y/n)")
    if is_draw_corr=='y': draw_corr(df, 'engulfxvol', 'trend')

is_exit = False
while not is_exit:
    main()
    is_exit = True if input("\nexit? (y/n)")=='y' else False








