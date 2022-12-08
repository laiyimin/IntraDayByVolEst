import datetime
import os.path
import sys
import numpy as np
import pandas as pd
import backtrader as bt
from pprint import pprint
import math
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os

# assign directory
directory = '1分K'
target_history = {}

# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        df = pd.read_csv(f)
        print("Read in " + f + "...")
        df.ts = pd.to_datetime(df.ts)
        df.rename(columns={'ts': 'datetime'}, inplace=True)
        df.set_index('datetime', inplace=True)

        # calculate signal
        print("Processing...")
        df = df.drop(columns=['Amount', 'Unnamed: 0', 'Open', 'Low', 'High'])
        df['前30分總和'] = df['Volume'].rolling(30).sum()
        df['InSignal'] = 0
        locs = df.index.indexer_at_time('09:30:00')
        wragling = df.iloc[locs]['前30分總和']
        wragling.index = wragling.index.date
        wragling = wragling.to_frame()
        wragling = wragling[~wragling.index.duplicated(keep='first')]  # 移除重複的 index
        wragling['前30分5日和'] = wragling['前30分總和'].rolling(5).sum()
        wragling['日量'] = df['Volume'].resample('D', closed="left").sum()
        wragling['5日量'] = wragling['日量'].rolling(5).sum()
        wragling['百分比'] = (wragling['前30分5日和'] / wragling['5日量']).shift(1)  # 後移一天，為了用來計算當日的預估量
        wragling['預測量'] = wragling['前30分總和'] / wragling['百分比']
        wragling['MA20'] = wragling['日量'].rolling(20).mean()
        wragling['InSignal'] = wragling['預測量'] > wragling['MA20'] * 5
        wragling = wragling.drop(columns=['前30分總和', '前30分5日和', '日量', '5日量', '百分比', '預測量', 'MA20'])

        # save
        stockID = f.removesuffix('.csv').removeprefix('1分K\\')
        print("Save " + stockID + " into target_history...")
        target_history[stockID] = wragling

np.save('所有標的訊號.npy', target_history)
print("Done!!")