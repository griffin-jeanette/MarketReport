# StockData.py

import requests
from requests.auth import HTTPBasicAuth
import alpha_vantage
import json
import pandas as pd
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as mpl
from datetime import datetime, timedelta
from bdateutil import isbday
import holidays
import time
from credentials import credentials
import import_ipynb
import ScrapedData

# Connects to an API and returns the response
def getData(URL, PARAMS):

    response = requests.get(url = URL, params = PARAMS)

    # If the response passes
    if response.status_code == 200:
        return response
    else:
        print("Error: " + response.status_code)

    return

# Converts a time in HH:MM format to an integer
def timeToNum(time):

    num = 0
    dec = 0
    num += int(time[1])

    if int(time[0]) != 0:
        num += 10

    dec += 10 * int(time[3]) + int(time[4])
    num += dec / 60

    return num

# Adds new columns named time and stamp to the dataframe.
# Time is an integer representation of a timestamp and
# stamp is the YYYY-MM-DD part of the timestamp
def newTime(df):

    newTime = []
    newStamp = []

    for i in range(len(df.index)):

        # create new decimal representation of time
        d = df["timestamp"][i]
        s = d[11:]
        s = timeToNum(s)
        newTime.append(s)

        # create new timestamp with only year-day-month
        stamp = d[:10]
        newStamp.append(stamp)

    df["time"] = newTime
    df["stamp"] = newStamp

    return

# Checks if today is a business day
def isBDay():

    today = datetime.now()

    return isbday(today, holidays = holidays.US())

# Gets the current day in YYYY-MM-DD format
def getDay():

    today = datetime.now()

    # create and return string representation of the date
    datestr = today.strftime("%Y-%m-%d")

    return datestr

# Gets the stock data for the current day
# Assumes today is a business day
def getDayData(df):

    # Get today's date and if it is a weekday
    today = getDay()

    df = df.loc[df["stamp"] == today]
    return df

# Creates plots of time vs closing value and time vs volume of
# a given dataframe
def generatePlots(df, ticker):

    # Plot time vs closing value
    df.plot(x = "time", y = "close")
    mpl.title("Daily Movement")
    mpl.ylabel("Price in USD")
    mpl.xlabel("Time")
    mpl.savefig(ticker + "DailyPrice.png")

    # Plot time vs volume
    df.plot(x = "time", y = "volume")
    mpl.title("Daily Volume")
    mpl.ylabel("Volume in USD")
    mpl.xlabel("Time")
    mpl.savefig(ticker + "DailyVolume.png")

    return

# Finds the percent difference between two numbers
def findChange(d):

    O = float(d["Open"].replace(".", "").replace(",", ""))
    C = float(d["Close"].replace(".", "").replace(",", ""))

    if C > O:
        diff = C / O
        diff -= 1

    else:
        diff = O / C
        diff = 1 - diff

    return diff * 100

# Find the value of the last close
def findLastClose(df):

    # Find the last business day
    dBefore = 1
    while not isbday((datetime.now() - timedelta(dBefore)), holidays = holidays.US()):
        dBefore += 1

    # create new df for that day and reindex
    datestr = (datetime.now() - timedelta(dBefore)).strftime("%Y-%m-%d")
    df = df.loc[df["stamp"] == datestr]
    df.index = pd.RangeIndex(len(df.index))

    return df.at[0, "close"]

# creates two images per ticker and then saves them as .png files
def createImages(tickers):

    key = credentials["AlphaVantage"]["key"]
    URL = "https://www.alphavantage.co/query"
    PARAMS = {"function": "TIME_SERIES_INTRADAY", "interval": "1min", "apikey": key, "datatype": "csv",
              "outputsize": "full"}

    T = ScrapedData.getInfo(tickers)
    if isBDay():

        for i in range(1, len(tickers) + 1):
            ticker = tickers[i - 1]
            print(ticker)
            PARAMS["symbol"] = ticker

            # API call, get content and decode
            r = getData(URL, PARAMS)
            currentTime = time.time()
            data = r.content
            newData = pd.read_csv(io.StringIO(data.decode("utf-8")))

            # Add new time column and then take the df only for a certain date
            newTime(newData)
            newDf = getDayData(newData)

            # If df is created successfully
            if len(newDf.index) != 0:
                generatePlots(newDf, ticker)

            # Alpha Vantage API max calls per minute is 5, wait so that
            # that is not exceeded
            if (i % 5) == 0:
                time.sleep(61 - ((time.time() - currentTime) % 60))


        mpl.close("all")

    for ticker in tickers:
        T[ticker][0]["Change"] =  findChange(T[ticker][0])

    return T
