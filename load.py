import os
import pytz
import numpy as np
import pandas as pd
import urllib.request
from datetime import datetime, timedelta

seoul = pytz.timezone('Asia/Seoul')

aws_dir = './output/AWS'
daily_dir = './output/daily'

def preprocess_df(df, kind=None):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['datetime'].dt.date)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    if kind == 'past':
        df['cumsum_rad'] = df.groupby('date')['rad'].cumsum() / 100000

    else:
        df['cumsum_rad'] = df['rad'].cumsum()/ 100000

    df['SVP'] = 0.61078 * np.exp(df['temp'] / (df['temp'] + 233.3) * 17.2694)
    df['VPD'] = df['SVP'] * (1 - df['hum'] / 100)

    return df


def today_data():
    date = datetime.now(seoul)
    Year = date.year
    Mon = f"{date.month:02d}"
    Day = f"{date.day:02d}"
    Site = 85
    Dev = 1

    aws_url =f'http://203.239.47.148:8080/dspnet.aspx?Site={Site}&Dev={Dev}&Year={Year}&Mon={Mon}&Day={Day}'
    data = urllib.request.urlopen(aws_url)

    df = pd.read_csv(data, header=None)

    df.columns = ['datetime', 'temp', 'hum', 'X', 'X', 'X', 'rad', 'wd', 'X', 'X', 'X', 'X', 'X', 'ws', 'rain', 'maxws', 'bv', 'X']
    drop_cols = [col for col in df.columns if 'X' in col]
    df = df.drop(columns=drop_cols)
    df = preprocess_df(df)
    return df


def past_data(sd, ed):
    df = pd.concat([pd.read_csv(os.path.join(aws_dir, file)) for file in os.listdir(aws_dir) if file.endswith('.csv') and pd.to_datetime(sd) <= pd.to_datetime(file.replace('.csv', ''), format='%Y%m%d') <= pd.to_datetime(ed)])
    df = preprocess_df(df, 'past')

    return df

def summary_data(sd, ed):
    df = pd.concat([pd.read_csv(os.path.join(daily_dir, file)) for file in os.listdir(daily_dir)])
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df[(df['date'] >= pd.to_datetime(sd)) & (df['date'] <= pd.to_datetime(ed))]
    df['date'] = df['date'].dt.date

    return df
