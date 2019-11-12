import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from sklearn.linear_model import LinearRegression
from io import StringIO
import base64


class market_impact:

    def __init__(self, comp):
        df = pd.read_csv('/Users/miazhang/flask-material-dashboard/app/data/' + comp + '.csv')
        df = df.replace({'null': np.nan})
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        df = df[df['Volume'] > 0].reset_index(drop=True)
        df = df[df['Date'] >= '2014-01-01'].reset_index(drop=True)
        df = df[['Date', 'Close', 'Volume']]
        self.df = df

    def get_I(self):
        df = self.df
        df['I'] = df['Close'].pct_change(periods=10)
        self.df = df

    def get_J(self):
        df = self.df
        df['Close*Volume'] = df['Close'] * df['Volume']
        df['Sum_of_Close*Volume'] = df['Close*Volume'].rolling(window=10).sum()
        df['Sum_of_Volume'] = df['Volume'].rolling(window=10).sum()
        df['S_bar'] = df['Sum_of_Close*Volume'] / df['Sum_of_Volume']
        df['S_0'] = df['Close'].shift(10)
        df['J'] = df['S_bar'] / df['S_0'] - 1
        df = df[['Date', 'Close', 'Volume', 'I', 'J']]
        self.df = df

    def get_X(self):
        df = self.df
        df['X'] = df['Volume'].rolling(window=10).sum()
        self.df = df

    def get_beta(self):
        df = self.df
        df['beta'] = 10 * df['Volume'].mean()
        self.df = df

    def get_r(self):
        df = self.df
        df['r'] = df['X'] / df['beta']
        self.df = df

    def temporary_impact_chart(self):
        df = self.df
        df = df[df['I'].notnull() & df['J'].notnull() & df['X'].notnull() & df['beta'].notnull() & df[
                'r'].notnull()].reset_index(drop=True)
        df['J - I/2'] = df['J'] - df['I'] / 2
        df = df[df['J - I/2'] > 0].reset_index(drop=True)
        df['ln_(J - I/2)'] = np.log(df['J - I/2'])
        df['ln_r'] = np.log(df['r'])
        df['ln_beta'] = np.log(df['beta'])
        df['x'] = df['ln_r'] + df['ln_beta']

        reg = LinearRegression().fit(df['x'].values.reshape(-1, 1), df['ln_(J - I/2)'])
        beta = reg.coef_[0]
        ln_eta = reg.intercept_
        score = reg.score(df['x'].values.reshape(-1, 1), df['ln_(J - I/2)'])

      #  img = StringIO.StringIO()
        plt.scatter(df['ln_r'], df['ln_(J - I/2)'], s=1)
        plt.plot(df['ln_r'], beta * df['x'] + ln_eta, color='red')
        plt.xlabel('ln(r) - sum 10 days’ vol / 10*avg 5years vol')
        plt.ylabel('ln(J - I/2) - ln(Temporary impact)')
        plt.title('Temporary impact ')
        plt.text(min(df['ln_r']), 0.8 * min(df['ln_(J - I/2)']), 'R-square = ' + str(score), color='red')
        plt.show()
    #  plt.savefig(img, format='png')
     #   plt.close()
     #   img.seek(0)
      #  plot_url = base64.b64encode(img.getvalue())
       # return plot_url

    def permanent_impact_chart(self):


        df = self.df
        df = df[df['I'].notnull() & df['J'].notnull() & df['X'].notnull() & df['beta'].notnull() & df['r'].notnull()].reset_index(drop = True)
        df = df[df['I'] > 0].reset_index(drop = True)
        df['ln_I'] = np.log(df['I'])
        df['ln_r'] = np.log(df['r'])
        df['ln_beta'] = np.log(df['beta'])
        df['x'] = df['ln_r'] + df['ln_beta']

        reg = LinearRegression().fit(df['x'].values.reshape(-1, 1), df['ln_I'])
        alpha = reg.coef_[0]
        ln_gamma = reg.intercept_
        score = reg.score(df['x'].values.reshape(-1, 1), df['ln_I'])


        plt.scatter(df['ln_r'], df['ln_I'], s = 1)
        plt.plot(df['ln_r'], alpha * df['x'] + ln_gamma, color = 'red')
        plt.xlabel('ln(r) - sum 10 days’ vol / 10*avg 5years vol')
        plt.ylabel('ln(I) - ln(Permernant impact)')
        plt.title('Permernant impact ')
        plt.text(min(df['ln_r']), 0.8 * min(df['ln_I']), 'R-square = ' + str(score), color = 'red')
        plt.show()