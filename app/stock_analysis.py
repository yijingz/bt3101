import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly
import json
from statsmodels.formula.api import ols

from app.preprocess import stock

def get_slope_no_intercept(df, y_name, x_name):
    results = ols(formula=y_name + " ~ " + x_name +" - 1", data=df).fit()
    slope = results.params[x_name]
    return slope

def preprocess_data(comp):
    data = stock(comp)

    data.convert_col_to_float(['Open', 'High', 'Low', 'Close', 'Volume'])
    data.keep_positive_val(['Volume'])
    data.create_lag_col(['Close'])
    data.create_rolling_mean_col(['Volume'], 20)
    data.create_lag_col(['Volume_prev_20_mean'])
    data.get_rid_of_null(['Volume_prev_20_mean'])

    data = data.df

    return data

def create_temp_perm_impact_col(data): #data is df
    data['Volume_ratio'] = data['Volume'] / data['Volume_prev_20_mean']
    data['Temporary_impact_buying'] = (data['High'] - data['Close']) / data['Close_prev']
    data['Temporary_impact_selling'] = (data['Low'] - data['Close']) / data['Close_prev']
    data['Permanent_impact'] = np.log(data['Close']) - np.log(data['Close_prev'])
    return data



def get_historical_chart(comp):
    from app import plot
    preprocessed_data = preprocess_data(comp)
    line = plot.px_line(preprocessed_data, "Date", "Close")
    lineJSON = plot.convert_chart_to_json(line)
    return lineJSON



def get_tempo_buying_chart(data):  #processed data
    data = create_temp_perm_impact_col(data)
    threshold = data['Volume_ratio'].quantile(0.8)
    data = data[data['Volume_ratio'] >= threshold].reset_index(drop=True)

    slope = get_slope_no_intercept(data, 'Temporary_impact_buying', 'Volume_ratio')
    line = list(map(lambda x: slope * x, data['Volume_ratio']))

    data['trend_line'] = line

    import plotly.express as px
    scatter = px.scatter(data, x="Volume_ratio", y="Temporary_impact_buying", trendline="ols", trendline_color_override="black")
    #scatter.add_scatter(data, x='Volume_ratio', y='Temporary_impact_buying')


    #scatter = dict(data=[dict(x=data['Volume_ratio'], y=data['Temporary_impact_buying'], type="scatter")], layout=dict(title='first graph'))


    #plot_data =go.Scatter(x=data['Volume_ratio'], y=data['Temporary_impact_buying'])

    graphJSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

  #  plt.scatter(data['Volume_ratio'], data['Temporary_impact_buying'])
   # plt.plot(data['Volume_ratio'], line, 'r', label='fitted line')
   # plt.show()



def get_market_impact_chart(df, x, y):
    pass


#data = preprocess_data('0002.HK')
#gjson = get_tempo_buying_chart(data)

