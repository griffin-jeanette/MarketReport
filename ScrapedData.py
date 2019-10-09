# ScrapedData.py

import requests
from bs4 import BeautifulSoup

# Returns the html of a given url
def getSoup(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup

# returns a dictionary of tickers where each value is
# a dictionary containing categories as keys and values as
# the category values, for example:
# {"AAPL": {"Market Cap (intraday)": "675.05B"...}...}
def getInfo(tickers):

    T = {}
    for ticker in tickers:
        D, keys, values = createDictionary2(ticker)
        T[ticker] = (D, keys, values)

    return T

# The function returns the data in a dictionary, with the key as the
# statistic name, and the value the value
def createDictionary2(ticker):

    url = "https://finance.yahoo.com/quote/" + ticker + "/p=" + ticker
    soup = getSoup(url)

    keys = []
    values = []
    D = {}

    k = soup.find_all("td", class_ = "C($primaryColor) W(51%)")
    v = soup.find_all("td", class_ = "Ta(end) Fw(600) Lh(14px)")
    close = soup.find("div", class_ = "My(6px) Pos(r) smartphone_Mt(6px)")

    close = close.div.span.text

    for i in range(len(k) - 1):
        if v[i].text == None:
            value = v[i].find("span", recursive = False)

        else:
            value = v[i].text
            #value = v[i].find("span", recursive = False)

        key = k[i].find("span", recursive = False)
        keys.append(key.text)
        values.append(value)

    keys.append("Close")
    values.append(close)

    for i in range(len(keys) - 1):
        D[keys[i]] = values[i]

    D["Close"] = close


    return (D, keys, values)

# Creates the dictionary holding stock data
def createDictionary(ticker):

    url = "https://finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker
    soup = getSoup(url)

    keys = []

    first = soup.find_all("td")
    for i in range(0, len(first) - 1, 2):
        item = first[i].find("span", recursive = False)
        keys.append(item)

    D = {}
    values = soup.find_all("td", class_ = "Fz(s) Fw(500) Ta(end)")
    for i in range(len(keys) - 1):
        D[keys[i].text] = values[i].text

    return D
