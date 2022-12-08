import os.path
import sys
import numpy as np
import backtrader as bt

def loadData(id, fromDate, toDate, minute=False):
    if minute:
        full_data = np.load('../datas/所有標的1分K.npy', allow_pickle='TRUE').item()
        dataframe = full_data[id]
        data = bt.feeds.PandasData(dataname=dataframe, fromdate=fromDate, todate=toDate, timeframe=bt.TimeFrame.Minutes)
    else:
        full_data = np.load('個股期標的歷史股價.npy', allow_pickle='TRUE').item()
        dataframe = full_data[id]
        dataframe.reset_index(inplace=True)
        dataframe.rename(columns={'Date': 'datetime'}, inplace=True)
        dataframe.drop(['Close'], axis=1)
        dataframe.rename(columns={'Adj Close':'close'}, inplace=True)
        dataframe.set_index('datetime', inplace=True)
        data = bt.feeds.PandasData(dataname=dataframe, fromdate=fromDate, todate=toDate)
    return data

def dumpMethod(obj):
    print(list(filter(lambda x: x[0] != '_' and callable(getattr(obj, x)), dir(obj))))