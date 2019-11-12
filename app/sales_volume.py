import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import plotly.express as px
import plotly
import json
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression


def preprocess_data(comp):
    data = pd.read_csv('/Users/miazhang/flask-material-dashboard/app/data/' + comp + '.csv')
    data = data.replace({'null': np.nan})
    data['Close'] = data['Close'].astype(float)
    data['Volume'] = data['Volume'].astype(float)
    data = data[data['Close'] > 0].reset_index(drop=True)
    data = data[data['Volume'] > 0].reset_index(drop=True)
    n = len(data['Volume'])

    # Calculate Y axis values
    data['Close_prev'] = data['Close'].shift(1)
    data['Close_log_return'] = np.log(data['Close']) - np.log(data['Close_prev'])

    data['sigma0'] = data['Close_log_return'].rolling(250).std()
    data['sigma'] = data['Close_log_return'].rolling(10).std()
    data['Y'] = np.log(data['sigma'] / data['sigma0'])

    # Calculate X axis values
    data['adtv'] = data['Volume'].rolling(250).mean()
    data['delta'] = data['Volume'].rolling(10).mean() / data['adtv']

    # Filter for only lare votatility (Y > 0)
    data = data[data['Y'] >= 0].reset_index(drop=True)

    data = data[data['Y'].notnull()].reset_index(drop=True)
    data = data[data['delta'].notnull()].reset_index(drop=True)
    return data


def get_slope_no_intercept(df, y_name, x_name):
    results = ols(formula=y_name + " ~ " + x_name +" - 1", data=df).fit()
    slope = results.params[x_name]
    return slope

def get_sales_df(dic):
    if dic['reminder_stocks'] > 0:
        vol_lst = [dic['daily_vol']] * (dic['days'] - 1) + [dic['reminder_stocks']]
    days_lst = [x for x in range(1, dic['days'] + 1)]
    sales_dic = {}
    sales_dic['Day'] = days_lst
    sales_dic['Shares'] = vol_lst
    df = pd.DataFrame(sales_dic)
    return df

def get_alpha_delta_adtv(comp, num):
    num = int(num)*100
    dic = {}
    data = preprocess_data(comp)

    alpha = get_slope_no_intercept(data, 'Y', 'delta')
    delta = 1 / ( 2 * alpha)
    adtv = sum(data['Volume'][-130:])/130

    daily_vol = delta * adtv
    days = int(num//daily_vol)


    dic['alpha'] = round(alpha, 4)
    dic['delta'] = round(delta, 4)
    dic['adtv'] = round(adtv, 2)
    dic['reminder_stocks'] = 0

    if num < daily_vol:
        dic['daily_vol'] = num
    else:
        dic['daily_vol'] = round(daily_vol, 1)

    if num % daily_vol > 0:
        dic['reminder_stocks'] = int(num % daily_vol)
        days += 1

    dic['days'] = days

    return dic

def get_sig_gamma_eta(comp):
    shares = pd.read_csv('/Users/miazhang/flask-material-dashboard/app/outstanding/process_total_shares.csv')

    def preprocess_data(comp):
        data = pd.read_csv('/Users/miazhang/flask-material-dashboard/app/data/' + comp + '.csv')
        data = data.replace({'null': np.nan})

        data['Close'] = data['Close'].astype(float)
        data
        data['Volume'] = data['Volume'].astype(float)
        data = data[data['Volume'] > 0].reset_index(drop=True)
        # data = data[(data['Date'] >= '2014-01-01')]
        data = data.reset_index()
        data = data.dropna()

        newdata = shares.loc[shares["Code"] == comp]
        data = data.merge(newdata, on="Date")

        return data

    # calculate permanent function
    def calculate_permanent(close_list):
        permanent = []
        for i in range(0, len(close_list) - 1):
            spost = close_list[i + 1]
            s0 = close_list[i]
            permanent.append((spost - s0) / s0)
        return permanent

    def calculate_realized(savg, close):
        realized = []
        for i in range(0, len(savg)):
            sbar = savg[i]
            realized.append((sbar - close[i]) / close[i])
        return realized

    def calculate_temporary(perm_list, realized_list):
        temp = []
        for (i, j) in zip(perm_list, realized_list):
            temp.append(i - 0.5 * j)
        return temp

    data = preprocess_data(comp)
    close = data["Close"]
    volume = data["Volume"]
    outstanding_shares = data["Shares Outstanding"]

    close_10days = []
    close_10days.append(close[0])
    sbar = []
    sum_vol_10days = []
    avg_out_shares_10days = []

    for i in range(1, len(data), 10):
        if len(data) - i < 10:
            break

        close_10days.append(close[i + 9])

        sum_vol = 0
        sum_vol_close = 0

        sum_vol_10days.append(sum(volume[i:i + 9]))
        avg_out_shares_10days.append(sum(outstanding_shares[i:i + 9]) / 10)

        for j in range(10):
            index = i // 10 + j
            sum_vol += volume[index]
            sum_vol_close += volume[index] * close[index]
        sbar.append(sum_vol_close / sum_vol)

    perm_impact = calculate_permanent(close_10days)
    realized_impact = calculate_realized(sbar, close_10days)
    sigma = float(np.std(perm_impact))

    perm_impact.append(0)
    realized_impact.append(0)
    sum_vol_10days.append(0)
    avg_out_shares_10days.append(0)

    df2 = {"perm_impact": perm_impact,
           "realized_impact": realized_impact,
           "sum_vol_10days": sum_vol_10days,
           "outstanding_shares": avg_out_shares_10days,
           "close_10days": close_10days,
           }

    df2 = pd.DataFrame(df2)
    df2["V"] = df2["sum_vol_10days"].rolling(window=10).mean()

    df2 = df2[df2['perm_impact'] < 0]
    df2 = df2.dropna()

    x_series = -1 * sigma * (df2["sum_vol_10days"] / df2["V"]) * ((df2["outstanding_shares"] / df2["V"]) ** 0.25)
    df2['X'] = x_series
    X = df2['X'].values.reshape(-1, 1)
    y = df2["perm_impact"].values.reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    slope = round(reg.coef_[0][0], 3)
    intercept = round(reg.intercept_[0], 3)
    r_2 = round(reg.score(X, y), 3)

    x_series_trans = -1 * sigma * (1 / df2["V"]) * ((df2["outstanding_shares"] / df2["V"]) ** 0.25)

    transformed_gamma = []
    latest_V = df2["V"].iloc[-1]
    for (a, b) in zip(close_10days, x_series_trans):
        transformed_gamma.append(slope * a * b)

    trans_gamma_avg = sum(transformed_gamma)/ float(len(transformed_gamma))

    eta2 = []
    eta1 = slope
    for i in range(df2.shape[0] - 1):
        X = df2['sum_vol_10days'].iloc[i]
        s0 = df2['close_10days'].iloc[i]
        spost = df2['close_10days'].iloc[i + 1]
        T = 1
        V = df2['V'].iloc[i]
        eta2.append(T / X * s0 * eta1 * sigma * (X / V / T) ** 0.6 + T / X * (spost - s0) / 2)
    avg_eta = sum(eta2) / len(eta2)

    output = {}
    output['sigma'] = sigma
    output['gamma'] = abs(trans_gamma_avg)
    output['eta'] = avg_eta

    return output



def get_trajectory(lamb, sig, gamma, eta, total_shares, T, tao=1):
    import math

    lamb = float(lamb)
    T = int(T)
    N = T / tao

    numerator = lamb * (sig ** 2)
    denominator = eta * (1 - gamma * tao / 2 / eta)
    k_bar_square = numerator / denominator
    cosh_k = k_bar_square * tao ** 2 / 2 + 1
    k = math.acosh(cosh_k) / tao

    x = [total_shares]
    for i in range(int(N)):
        try:
            x.append((math.sinh((T - (i + 1) * tao) * k) / math.sinh(T * k)) * total_shares)
        except:
            x.append(math.exp(- (i + 1) * tao * k) * total_shares)
    for index in range(len(x)):
        if x[index] < 0.0001 * total_shares:
            x[index] = sum(x[index:])
            del x[index + 1:]
            break
    return x

def get_optimal_sales_df(x, total_shares, T, tao=1):
    T = int(T)
    N = T / tao

    sales_vol = []
    sales_sum = 0
    for i in range(int(N)):
        try:

            remaining = x[i]
            sales_vol.append(int(total_shares - remaining - sales_sum))
            sales_sum += int(total_shares - remaining - sales_sum)
        except:
            pass

    df = pd.DataFrame(list(zip(x, sales_vol)), columns=['Position Shares', 'Sold Shares'])
    return df

def get_optimal_cost(x, gamma, X, spread, eta, tao=1):
    opt_shortfall = 1 / 2 * gamma * X ** 2
    for i in range(len(x) - 1):
        n = x[i] - x[i + 1]
        opt_shortfall += spread * abs(n) + (eta - 1 / 2 * gamma * tao) / tao * n ** 2
    return round(opt_shortfall, 2)

def get_additional_cost(delta, x, gamma, X, eta, spread, optimal_cost, tao=1):
    add_cost = []
    import random
    all_real_x = []
    ex_shortfall_list = []
    avg_real_x = []
    shortfall_list = []
    shortfall_list_delta = []
    for m in range(1000):
        step_shortfall_list = []
        real_x_list = []
        shortfall = 1 / 2 * gamma * X ** 2
        for i in range(len(x)):  ##one trajectory adding random number
            rand_num = random.gauss(0, delta)
            real_x = x[i] * (1 + rand_num)
            real_x_list.append(real_x)
            if i > 0:
                n = real_x_list[-2] - real_x
                shortfall += spread * abs(n) + (eta - 1 / 2 * gamma * tao) / tao * n ** 2
                step_shortfall_list.append(spread * abs(n) + (eta - 1 / 2 * gamma * tao) / tao * n ** 2)
        all_real_x.append(real_x_list)
        ex_shortfall_list.append(shortfall)
        shortfall_list.append(step_shortfall_list)
    avg_shortfall = sum(ex_shortfall_list) / len(ex_shortfall_list)
    add_cost.append(avg_shortfall - optimal_cost)

    return round(add_cost[-1], 2)

def get_new_traj(delta, x, gamma, X, eta, spread, optimal_cost, tao=1):
    add_cost = []
    import random
    all_real_x = []
    ex_shortfall_list = []
    avg_real_x = []
    shortfall_list = []
    shortfall_list_delta = []
    for m in range(1000):
        step_shortfall_list = []
        real_x_list = []
        shortfall = 1 / 2 * gamma * X ** 2
        for i in range(len(x)):  ##one trajectory adding random number
            rand_num = random.gauss(0, delta)
            real_x = x[i] * (1 + rand_num)
            real_x_list.append(real_x)
            if i > 0:
                n = real_x_list[-2] - real_x
                shortfall += spread * abs(n) + (eta - 1 / 2 * gamma * tao) / tao * n ** 2
                step_shortfall_list.append(spread * abs(n) + (eta - 1 / 2 * gamma * tao) / tao * n ** 2)
        all_real_x.append(real_x_list)
        ex_shortfall_list.append(shortfall)
        shortfall_list.append(step_shortfall_list)
    avg_shortfall = sum(ex_shortfall_list) / len(ex_shortfall_list)
    add_cost.append(avg_shortfall)

    for i in range(len(shortfall_list[0])):  # get average shortfall
        sf_sum = 0
        for j in range(len(shortfall_list)):  ##1000
            sf_sum += shortfall_list[j][i]

        shortfall_list_delta.append(sf_sum / len(shortfall_list))

    for j in range(len(all_real_x[0])):  # get average trajectory
        x_sum = 0
        for n in range(len(all_real_x)):
            x_sum += all_real_x[n][j]
        avg_real_x.append(x_sum / len(all_real_x))

    print(avg_real_x)

    return avg_real_x, round(add_cost[-1], 2)




def get_sales_chart(df):
    from app import plot
    bar = plot.px_bar(df, x=df.index.name, y='Sold Shares', width=700, height=400, text='Sold Shares', title_text='Number of Shares to Sell Daily', color='Sold Shares')
    barjson = plot.convert_chart_to_json(bar)

    return barjson

def get_position_chart(df):
    from app import plot
    bar = plot.px_bar(df, x=df.index.name, y='Position Shares', width=700, height=400, text='Position Shares',
                      title_text='Number of Shares Remaining Daily')
    position_barjson = plot.convert_chart_to_json(bar)

    return position_barjson

def get_daily_sales_dic(df):
    dic  = {}
    for index, row in df.iterrows():
        dic['Day ' + str(index)] = row['Sold Shares']
    return dic