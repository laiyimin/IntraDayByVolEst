# import pandas as pd
# import numpy as np

# byMinute: 用當日的前幾分鐘的量來預估
# byDays: 以前幾日為基準預估
# MA, Multiplier: 當天預估量為 MA 日線的 Multiplier 倍，則發出訊號

def getSignal(assetId, byMinute=30, byDays=5, ma=20, multiplier=5):
    full_data = np.load('../datas/所有標的1分K.npy', allow_pickle='TRUE').item()
    df = full_data[assetId]
    df = df.drop(columns=['Amount','Unnamed: 0','Open','Low','High'])
    df['前30分總和'] = df['Volume'].rolling(byMinute).sum()
    df['InSignal']=0

    locs=df.index.indexer_at_time('09:30:00')
    wragling = df.iloc[locs]['前30分總和']
    wragling.index=wragling.index.date
    wragling = wragling.to_frame()
    wragling = wragling[~wragling.index.duplicated(keep='first')]  #移除重複的 index

    wragling['前30分5日和'] = wragling['前30分總和'].rolling(byDays).sum()
    wragling['日量']=df['Volume'].resample('D', closed="left").sum()
    wragling['5日量']=wragling['日量'].rolling(byDays).sum()
    wragling['百分比']=(wragling['前30分5日和']/wragling['5日量']).shift(1) # 後移一天，為了用來計算當日的預估量
    wragling['預測量']=wragling['前30分總和']/wragling['百分比']
    wragling['MA20']=wragling['日量'].rolling(ma).mean()
    wragling['InSignal']=wragling['預測量']>wragling['MA20']*multiplier
    wragling['InSignal']=wragling['InSignal'].astype(int)  # 將 True/False 轉換成 1/0
    wragling.index=pd.to_datetime(wragling.index.values) + pd.to_timedelta('09:30:00')   # 為了在下一行合併，幫 wragling 的時間加上日期
    df['InSignal'].update(wragling['InSignal'])  # 將 wragling 裡算出來的訊號合併至 df
    df = df.drop(columns=['前30分總和'])
    return df