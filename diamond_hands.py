import selenium
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import smtplib, ssl
import time
import pandas as pd
import json
import yfinance as yf

def get_meme_stocks():
    url = "https://www.wsbtrending.com/"
    class_name = 'MuiTypography-root.MuiTypography-body1'
    driver = webdriver.Chrome()
    driver.get(url)
    memes_text = driver.find_elements_by_class_name(class_name)
    memes_text = [m.text for m in memes_text if '(' in m.text and ')' in m.text]
    driver.close()
    return memes_text

def process_meme_stocks(memes_text, start=5, end=20):
    total_viral = 0
    memes_dict = {}
    for m in memes_text[start:end]:
        symbol, viral = m.split(' ')
        viral = int(viral[1:-1])
        price = yf.Ticker(symbol).info['regularMarketPrice']
        memes_dict[symbol] = [viral, price]
        total_viral += viral
    return memes_dict

def update_portfolio(portfolio, memes, thresh=1.2):
    cash = portfolio['cash']
    
    # sell
    for k in memes:
        if k in portfolio:
            mv, mp = memes[k]
            sell_idx = []
            for i, purchase in enumerate(portfolio[k]):
                pv, pp, ps = purchase
                if mp/pp > thresh or mv/pv > thresh:
                    sell_idx.append(i)
                    cash += mp*ps
            new_portfolio = [p for j, p in enumerate(portfolio[k]) if j not in sell_idx]
            portfolio[k] = sorted(new_portfolio, key=lambda x: -x[1]*x[2])
            
    total_viral = 0
    for k in memes:
        total_viral += memes[k][0]
        
    # buy
    spending = 0
    for k in memes:
        v, p = memes[k]
        alloc_cash = cash * (v / total_viral)
        num_shares = int(alloc_cash/p)
        if num_shares > 0:
            if k not in portfolio:
                portfolio[k] = []
            portfolio[k].append([v, p, num_shares])
            spending += p*num_shares
    
    portfolio['cash'] = cash-spending
    return portfolio

def get_total_assets(portfolio):
    total = 0
    for k in portfolio:
        if k=="cash":
            total += portfolio[k]
        else:
            for p in portfolio[k]:
                total += p[1]*p[2]
    return total

if __name__ == "__main__":
    portfolio = {'cash': 1000}

    while True:
        m_text = get_meme_stocks()
        m_dict = process_meme_stocks(m_text)
        portfolio = update_portfolio(portfolio, m_dict, thresh=1.2)
        print(get_total_assets(portfolio))
        time.sleep(10800)
    
