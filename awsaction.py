import os
import pytz
import pandas as pd
import urllib.request
from datetime import datetime, timedelta

desired_timezone = pytz.timezone('Asia/Seoul')

def get_aws(date):
    Site = 85
    Dev = 1
    Year = date.year
    Mon = f"{date.month:02d}"
    Day = f"{date.day:02d}"

    aws_url =f'http://203.239.47.148:8080/dspnet.aspx?Site={Site}&Dev={Dev}&Year={Year}&Mon={Mon}&Day={Day}'
    data = urllib.request.urlopen(aws_url)

    df = pd.read_csv(data, header=None)
    df.columns = ['datetime', 'temp', 'hum', 'X', 'X', 'X', 'rad', 'wd', 'X', 'X', 'X', 'X', 'X', 'ws', 'rain', 'maxws', 'bv', 'X']
    drop_cols = [col for col in df.columns if 'X' in col]
    df = df.drop(columns=drop_cols)

    return df

def main():
    date = datetime.now(desired_timezone) - timedelta(days=1)
    df = get_aws(date)
    filename = f"./output/AWS/{date.date().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False)

if __name__ == '__main__':
    main()
