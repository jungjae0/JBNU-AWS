import os
import pytz
import pandas as pd
import urllib.request
from datetime import datetime, timedelta
from astral.sun import sun
from astral import LocationInfo

desired_timezone = pytz.timezone('Asia/Seoul')
daily_dir = './output/daily'
aws_dir = './output/AWS'

def save_aws(date):
    Site = 85
    Dev = 1
    Year = date[0:4]
    Mon = date[4:6]
    Day = date[6:8]

    aws_url =f'http://203.239.47.148:8080/dspnet.aspx?Site={Site}&Dev={Dev}&Year={Year}&Mon={Mon}&Day={Day}'
    data = urllib.request.urlopen(aws_url)

    df = pd.read_csv(data, header=None)
    df.columns = ['datetime', 'temp', 'hum', 'X', 'X', 'X', 'rad', 'wd', 'X', 'X', 'X', 'X', 'X', 'ws', 'rain', 'maxws', 'bv', 'X']
    drop_cols = [col for col in df.columns if 'X' in col]
    df = df.drop(columns=drop_cols)

    filename = os.path.join(aws_dir, f"{date}.csv")
    df.to_csv(filename, index=False)

    return df

def change_timeobj(suntime_str):
    suntime = datetime.strptime(str(suntime_str), '%Y-%m-%d %H:%M:%S.%f%z')
    suntime = suntime.replace(second=0, microsecond=0)
    suntime = suntime.strftime('%Y-%m-%d %H:%M:%S')

    return suntime

def get_suntime(date):
    date_obj = datetime.strptime(date, '%Y%m%d')

    city = LocationInfo("Jeonju", "South Korea", "Asia/Seoul", 35.848, 127.135)
    city_timezone = pytz.timezone(city.timezone)

    sr = sun(city.observer, date=date_obj - timedelta(days=1))
    ss = sun(city.observer, date=date_obj)

    sunrise_time = sr["sunrise"].astimezone(city_timezone)
    sunset_time = ss["sunset"].astimezone(city_timezone)

    sunrise_datetime = change_timeobj(sunrise_time)
    sunset_datetime = change_timeobj(sunset_time)

    return sunrise_datetime, sunset_datetime

def summary(df, date):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['cumsum_rad'] = df['rad'].cumsum()
    df['cumsum_rad'] = df['cumsum_rad'] / 100000

    tmin = df['temp'].min()
    tmax = df['temp'].max()
    tavg = round(df['temp'].mean(), 1)
    trange = round(tmax-tmin, 1)

    sunrise_datetime, sunset_datetime = get_suntime(date)
    sunrise_time  = sunrise_datetime.split(' ')[-1]
    sunset_time = sunset_datetime.split(' ')[-1]
    sunrise_rows = df[(df['datetime'] > sunrise_datetime) & (df['datetime'] < sunset_datetime)]
    sunset_rows = df[~df.index.isin(sunrise_rows.index)]

    sunrise_temp_mean = sunrise_rows['temp'].mean()
    sunset_temp_mean = sunset_rows['temp'].mean()

    sun_time = pd.to_datetime(str(sunset_datetime)) - pd.to_datetime(str(sunrise_datetime))
    sun_time = str(sun_time).split('days')[-1].strip()
    DIF = round(sunrise_temp_mean - sunset_temp_mean, 1)

    rain = df['rain'].sum()
    cumsum_rad = round(df['cumsum_rad'].max(), 1)


    values = [date, tavg, tmin, tmax, trange, DIF, rain, cumsum_rad, sunrise_time, sunset_time, sun_time]
    summary = pd.DataFrame([values], columns=['date', 'tavg', 'tmin', 'tmax', 'trange', 'DIF', 'rain', 'rad', 'sunrise', 'sunset',
                                              'suntime'])
    return summary

def save_summary(df, date):

    ym = date[0:6]

    summary_df = summary(df, date)

    save_path = os.path.join(daily_dir, f'{ym}.csv')
    if os.path.exists(save_path):
        exists_df = pd.read_csv(save_path)
        summary_df = pd.concat([exists_df, summary_df])

    else:
        summary_df = summary_df
    summary_df['date'] = summary_df['date'].astype(int)
    summary_df = summary_df.sort_values(by='date', ascending=True)
    summary_df = summary_df.drop_duplicates()

    summary_df.to_csv(save_path, index=False)

def save_retry(re_date):
    re_filepath = os.path.join(aws_dir, f"{re_date}.csv")
    if not os.path.exists(re_filepath):
        df = save_aws(re_date)
    else:
        df = pd.read_csv(re_filepath)
    save_summary(df, re_date)

def main():
    # re_date = '20240109'  # %Y%m%d
    # save_retry(re_date)
    date = datetime.now(desired_timezone) - timedelta(days=1)
    date = date.date().strftime('%Y%m%d')

    df = save_aws(date)
    save_summary(df, date)

if __name__ == '__main__':
    main()
