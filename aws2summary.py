import os
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def get_date_list(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    date_list = []

    while start_date <= end_date:
        date_list.append(start_date.strftime("%Y%m%d"))
        start_date += timedelta(days=1)

    return date_list


def raw_dataframe(folder_path, date_list):
    df_list = [pd.read_csv(os.path.join(folder_path, date + '.csv')) for date in date_list]
    df = pd.concat(df_list)

    return df


def minute_dataframe(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['datetime'].dt.date)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    return df


def hour_dataframe(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['datetime'].dt.date)
    df['hour'] = df['datetime'].dt.hour

    df = df.groupby(['date', 'hour']).mean().reset_index()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['datetime'] = df['date'] + pd.to_timedelta(df['hour'].astype(str) + ':00:00')
    return df


def get_dataframe(start_date_str, end_date_str, folder_path):
    date_list = get_date_list(start_date_str, end_date_str)
    df = raw_dataframe(folder_path, date_list)
    minute_df = minute_dataframe(df)
    hour_df = hour_dataframe(df)

    return minute_df, hour_df


def rain_rank(x):
    if 0 < x < 1.0:
        return '0.1mm 이상 1.0mm 미만'
    elif 1.0 <= x < 10.0:
        return '1.0mm 이상 10.0mm 미만'
    elif 10.0 <= x < 30.0:
        return '10.0mm 이상 30.0mm 미만'
    elif 30.0 <= x:
        return '30.0mm 이상'
    else:
        return '무강수'


def wd_cate(x):
    directions = ["북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동", "남", "남남서", "남서", "서남서", "서", "서북서", "북서", "북북서"]
    index = int((x + 11.25) / 22.5) % 16
    return directions[index]


def daily_data(minute_df, hour_df):
    hour_df, minute_df = hour_df.copy(), minute_df.copy()
    # 1. 일별 통계
    summary = minute_df.groupby('date').agg(tavg=('temp', 'mean'),
                                            tmax=('temp', 'max'),
                                            tmin=('temp', 'min'),
                                            rain=('rain', 'sum'),
                                            rmax=('rad', 'max'),).reset_index()
    summary['temp_gap'] = summary['tmax'] - summary['tmin']

    # 2-1. 강수일수: 일강수량이 0.1mm 이상인 날의 수
    summary['강수일수'] = summary['rain'].apply(lambda x: 1 if x > 0.1 else 0).cumsum()

    # 2-2. 폭염일수: 일 최고기온이 33℃ 이상인 날의 수
    summary['폭염일수'] = summary['tmax'].apply(lambda x: 1 if x > 33 else 0).cumsum()

    # 2-3. 한파일수: 아침 최저기온(03:01~09:00)이 영하 12℃ 이하인 날의 수 -> 10월 ~ 익년 4월
    summary['한파일수'] = summary['tmin'].apply(lambda x: 1 if x < -12 else 0).cumsum()

    # 3-1. 강수 계급별일수
    summary['강수계급'] = summary['rain'].apply(rain_rank)

    # 3-2. 바람 계급별일수: 각 풍향의 풍속 계급별 빈도
    hour_df['풍향'] = hour_df['wd'].apply(wd_cate)
    wd_category = hour_df[['date', '풍향']]
    # wd_category = hour_df.groupby(['date'])['풍향'].value_counts().reset_index(name='counts')
    #
    # wd_category = wd_category.pivot(index='date', columns='풍향', values='counts')
    # wd_category = wd_category.fillna(0)

    # 4-1. 체감온도 -> 여름철(5~9월)과 겨울철(10~익년 4월)
    # 4-1-1. 여름철 체감온도: 일 최고 체감온도
    # 4-1-2. 겨울철 체감온도: 일 최저 체감온도 -> 기온 10℃ 이하, 풍속 1.3m/s 이상
    to_hotcold = minute_df
    to_hotcold['Tw'] = to_hotcold['temp'] * np.arctan((0.151977 * ((to_hotcold['hum'] + 8.313659) ** 0.5))) + \
                       np.arctan(to_hotcold['temp'] + to_hotcold['hum']) - np.arctan(to_hotcold['hum'] - 1.67633) + \
                       0.00391838 * (to_hotcold['hum'] ** 1.5) * np.arctan(0.023101 * to_hotcold['hum']) - 4.686035
    to_hotcold['hot'] = -0.2442 + 0.55399 * to_hotcold['Tw'] + 0.45535 * to_hotcold['temp'] - 0.0022 * (
                to_hotcold['Tw'] ** 2) + 0.00278 * to_hotcold['Tw'] * to_hotcold['temp'] + 3.0
    to_hotcold['cold'] = 13.12 + 0.6214 * to_hotcold['temp'] - 11.37 * to_hotcold['ws'] ** 0.16 + 0.3965 * to_hotcold[
        'ws'] ** 0.16 * to_hotcold['temp']
    to_hotcold['cold'] = to_hotcold.apply(lambda row: row['cold'] if row['temp'] < 11 and row['ws'] > 1.2 else '-',
                                          axis=1)
    hot_cold = to_hotcold.groupby('date').agg(hot=('hot', 'max'), cold=('cold', 'min'), ).reset_index()
    hot_cold['month'] = pd.to_datetime(hot_cold['date']).dt.month
    hot_cold['ts'] = hot_cold.apply(lambda row: row['hot'] if row['month'] in [5, 6, 7, 8, 9] else row['cold'], axis=1)
    hot_cold = hot_cold[['date', 'ts']]

    # 4-2. 실효습도: 상대습도에 경과 시간에 따른 가중치 주어 건조를 나타내는 지수
    hd = minute_df[['date', 'hum']]
    hd = hd.groupby('date')['hum'].mean().reset_index()
    r = 0.7
    for i in range(0, 5):
        hd[f'h{i}d'] = hd['hum']
        if i != 0:
            hd[f'h{i}d'] = hd['hum'].shift(i) * r ** i

    hd['he'] = (1 - r) * hd[['h0d', 'h1d', 'h2d', 'h3d', 'h4d']].sum(axis=1)
    hd['he'] = hd['he'].apply(lambda x: format(x, '.6f'))
    hd = hd[['date', 'he']]

    # 4-3. 적산온도
    summary['적산온도'] = summary['tavg'].apply(lambda x: x - 5 if x >= 5 else 0).cumsum()

    daily_df = pd.merge(summary, hot_cold, on='date', how='inner')
    daily_df = pd.merge(daily_df, hd, on='date', how='inner')
    col_rename = {'date':'날짜', 'tavg':'평균기온', 'tmax':'최고기온', 'tmin':'최저기온',
                  'rain':'강수량','rmax':'최대일사','temp_gap':'일교차','ts':'체감온도', 'he':'실효습도'}
    daily_df = daily_df.rename(columns=col_rename)
    float_cols = daily_df.select_dtypes(include=['float']).columns
    daily_df[float_cols] = daily_df[float_cols].round(2)

    return daily_df, wd_category

def weekly_date(df):
    df['날짜'] = df['날짜'].astype(str)
    max_tavg = dict(df.iloc[df['평균기온'].idxmax()][['날짜', '평균기온']])
    min_tavg = dict(df.iloc[df['평균기온'].idxmin()][['날짜', '평균기온']])
    max_tmax = dict(df.iloc[df['최고기온'].idxmin()][['날짜', '최고기온']])
    min_tmin = dict(df.iloc[df['최저기온'].idxmin()][['날짜', '최저기온']])
    rain_date = ', '.join(df[df['강수계급'] != '무강수']['날짜'].tolist())

    dates_dict = {'최고 평균기온': max_tavg, '최저 평균기온': min_tavg,
                  '최고 최고기온': max_tmax, '최저 최저기온': min_tmin,
                  '강수일': rain_date}

    data_list = []
    for key, value in dates_dict.items():
        if '날짜' in value:
            data_list.append(
                {'구분': key, '날짜': value['날짜'], '값': value.get('평균기온', value.get('최고기온', value.get('최저기온')))})
        else:
            data_list.append({'구분': key, '날짜': value})
    df = pd.DataFrame(data_list)

    return df