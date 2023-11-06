import os
import pytz
import pandas as pd
import urllib.request as urllib2
from datetime import datetime, timedelta

desired_timezone = pytz.timezone('Asia/Seoul')

def get_date_list(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    date_list = []

    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)

    return date_list

def get_aws(date):
    Site = 85
    Dev = 1
    Year = date.year
    Mon = f"{date.month:02d}"
    Day = f"{date.day:02d}"

    aws_url =f'http://203.239.47.148:8080/dspnet.aspx?Site={Site}&Dev={Dev}&Year={Year}&Mon={Mon}&Day={Day}'
    data = urllib2.urlopen(aws_url)

    df = pd.read_csv(data, header=None)
    df.columns = ['datetime', 'temp', 'hum', 'X', 'X', 'X', 'rad', 'wd', 'X', 'X', 'X', 'X', 'X', 'ws', 'rain', 'maxws', 'bv', 'X']
    drop_cols = [col for col in df.columns if 'X' in col]
    df = df.drop(columns=drop_cols)
    return df

def save_aws(start_date_str, end_date_str):
    date_list = get_date_list(start_date_str, end_date_str)

    for date in date_list:
        str_date = date.strftime("%Y%m%d")
        filename = f'./output/AWS/{str_date}.csv'
        each_data = get_aws(date)
        each_data.to_csv(filename, index=False)


def main():
    start_date_str = "20231101"
    end_date_str = "20231106"

    save_aws(start_date_str, end_date_str)

if __name__ == '__main__':
    main()
