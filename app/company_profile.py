import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def get_profile_parser(comp):
    url = 'https://sg.finance.yahoo.com/quote/{}/profile?p={}'.format(comp, comp)
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')
    return soup

def get_company_name(comp):
    url = 'https://sg.finance.yahoo.com/quote/{}/profile?p={}'.format(comp, comp)
    r = requests.get(url)
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')

    company = soup.find('h1', {'data-reactid': '7'})
    indus = ''
    try:
        indus = soup.findAll('span', {'class': 'Fw(600)'})[1]
    except:
        pass
    return company.text, indus.text


def get_historical_price_summary(comp):
    dic = {}
    data = pd.read_csv('/Users/miazhang/flask-material-dashboard/app/data/' + comp + '.csv')
    dic['start_date'] = data.iloc[0]['Date']
    dic['start_price'] = data.iloc[0]['Open']
    dic['end_date'] = data.iloc[-1]['Date']
    dic['end_price'] = data.iloc[-1]['Close']
    dic['mean_close'] = round(data['Close'].mean(), 2)
    sigma = data['Close'].std()


    data = data.replace({'null': np.nan})
    data['Close'] = data['Close'].astype(float)
    data['Volume'] = data['Volume'].astype(float)
    data = data[data['Volume'] > 0].reset_index(drop=True)

    data['Close_prev'] = data['Close'].shift(1)
    data['Close_log_return'] = np.log(data['Close']) - np.log(data['Close_prev'])
    min_value = data['Volume'].min()
    max_value = data['Volume'].max()
    data['Normalized_Volume'] = (data['Volume'] - min_value) / (max_value - min_value)

    data = data[data['Close_log_return'].notnull() & data['Normalized_Volume'].notnull()].reset_index(drop=True)
    dic['log_mean']= round(data['Close_log_return'].mean(), 4)
    dic['log_sigma']= round(data['Close_log_return'].std(), 4)


    dic['sigma'] = round(sigma, 2)
    return dic

#soup = get_profile_parser('0002.HK')
#print(get_historical_price_summary('0002.HK'))
