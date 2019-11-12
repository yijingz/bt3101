import pandas as pd
import numpy as np

class stock:
    def __init__(self, comp):
        df = pd.read_csv('app/data/'+ comp + '.csv')
        self.df = df.replace({'null': np.nan})

    def get_rid_of_null(self, col_lst):
        df = self.df
        for col in col_lst:
            df[df[col].notnull()].reset_index(drop=True)
        self.df = df

    def convert_col_to_float(self, col_lst):
        df = self.df
        for col in col_lst:
            df[col] = df[col].astype(float)
        self.df = df

    def keep_positive_val(self, col_lst, drop_index=True):
        df = self.df
        for col in col_lst:
            df = df[df[col] > 0].reset_index(drop=drop_index)
        self.df = df

    def create_lag_col(self, col_lst):
        df = self.df
        for col in col_lst:
            df[col + '_prev'] = df[col].shift(1)
        self.df = df

    def create_rolling_mean_col(self, col_lst, num):
        df = self.df
        for col in col_lst:
            df[col + '_prev_' + str(num) + '_mean'] = df.Volume.rolling(window=num).mean()
            df[col + '_prev_' + str(num) + '_mean'] = df[col + '_prev_' + str(num) + '_mean'].shift(1)
        self.df = df
