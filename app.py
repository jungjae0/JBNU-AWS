import copy
import os

import pytz
import aws2summary
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

seoul = pytz.timezone('Asia/Seoul')

def min_max_date(folder_path):
    csv_list = os.listdir(folder_path)
    csv_list = [int(filename.split('.')[0]) for filename in csv_list]
    max_value = str(max(csv_list))
    min_value = str(min(csv_list))

    min_date = datetime(int(min_value[:4]), int(min_value[4:6]), int(min_value[6:]))
    max_date = datetime(int(max_value[:4]), int(max_value[4:6]), int(max_value[6:]))

    max_date1 = max_date - timedelta(days=2)
    max_date2 = max_date - timedelta(days=1)

    return min_date, max_date1, max_date2

def week_temp_line(df):
    # fig = px.line(df, x='datetime', y='temp', title='Temperature Over Time')
    max_temp = df['temp'].max()
    min_temp = df['temp'].min()

    fig = go.Figure(data=[go.Scatter(x=df["datetime"], y=df['temp'], name='temp')])
    fig.update_layout(xaxis={"rangeslider": {"visible": True}, "type": "date",
                             "range": [df["datetime"].min(), df["datetime"].max()]})

    fig.add_trace(go.Scatter(x=[pd.to_datetime(df[df['temp'] == max_temp]['datetime'].values[0])],
                             y=[max_temp],
                             mode='markers',
                             marker=dict(size=10, color='red'),
                             name='최고온도'))
    fig.add_trace(go.Scatter(x=[pd.to_datetime(df[df['temp'] == min_temp]['datetime'].values[0])],
                             y=[min_temp],
                             mode='markers',
                             marker=dict(size=10, color='blue'),
                             name='최저온도'))
    fig.update_layout(title_text=f'{df["datetime"].min().date()} ~ {df["datetime"].max().date()}')

    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='온도(℃)')

    return fig

def day_temp_line(df, select_date):
    df = df[df['datetime'].dt.date == pd.to_datetime(select_date)]
    fig = go.Figure(data=[go.Scatter(x=df["datetime"], y=df['temp'], name='temp')])
    fig.update_layout(title_text='온도')
    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='온도(℃)')
    return fig

def day_humid_line(df, select_date):
    df = df[df['datetime'].dt.date == pd.to_datetime(select_date)]
    fig = go.Figure(data=[go.Scatter(x=df["datetime"], y=df['hum'], name='hum')])
    fig.update_layout(title_text='습도')
    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='습도(%)')

    return fig

def day_temphumid_line(df, select_date):
    df = df[df['datetime'].dt.date == pd.to_datetime(select_date)]
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["datetime"], y=df['temp'], mode='lines', name='temp', line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=df["datetime"], y=df["hum"], name='hum', mode='lines', yaxis='y2', marker=dict(color='orange')))

    fig.update_layout(yaxis=dict(title='온도(℃)'))
    fig.update_layout(yaxis2=dict(title='습도(%)', overlaying='y', side='right', showgrid=False))
    fig.update_xaxes(title_text='날짜')

    fig.update_yaxes(range=[0, 100], tick0=0, dtick=10, secondary_y=True)


    return fig

def day_rad_line(df, select_date):
    df = df[df['datetime'].dt.date == pd.to_datetime(select_date)]
    df['cumsum_rad'] = df['rad'].cumsum()
    fig = go.Figure(data=[go.Scatter(x=df["datetime"], y=df['cumsum_rad'], name='hum')])
    fig.update_layout(title_text='누적광량')
    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='누적광량(W/m²)')

    return fig


def daily_temprain_linebar(df):

    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df["날짜"], y=df['평균기온'], mode='lines', name='평균온도', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df["날짜"], y=df['최저기온'], mode='lines', name='최저온도', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df["날짜"], y=df['최고기온'], mode='lines', name='최고온도', line=dict(color='red')))

    fig.add_trace(go.Bar(x=df["날짜"], y=df["강수량"], name='강수량(mm)', yaxis='y2', marker=dict(color='blue')))

    fig.update_layout(yaxis=dict(title='온도 (℃)'))

    fig.update_layout(yaxis2=dict(title='강수량', overlaying='y', side='right', showgrid=False))
    fig.update_yaxes(range=[0, 100], tick0=0, dtick=10, secondary_y=True)

    return fig

def daily_tempdiff_line(df):

    fig = go.Figure(data=[go.Scatter(x=df["날짜"], y=df['일교차'], name='일교차', mode='lines')])

    fig.update_layout(title_text='일교차')
    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='일교차(℃)')

    return fig

def rain_count_pie(df):
    grouped_data = df.groupby('강수계급').size().reset_index(name='갯수')
    fig = px.pie(grouped_data, names='강수계급', values='갯수', title='강수계급별 분포',
                 hover_data=['강수계급', '갯수'])
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig

def text_to_degrees(text_direction):
    direction_mapping = {
        "북": 0,
        "북북동": 22.5,
        "북동": 45,
        "동북동": 67.5,
        "동": 90,
        "동남동": 112.5,
        "남동": 135,
        "남남동": 157.5,
        "남": 180,
        "남남서": 202.5,
        "남서": 225,
        "서남서": 247.5,
        "서": 270,
        "서북서": 292.5,
        "북서": 315,
        "북북서": 337.5
    }

    return direction_mapping.get(text_direction, None)

def wd_count_pie(df):
    # grouped_data = df.groupby('풍향').size().reset_index(name='갯수')
    # fig = px.pie(grouped_data, names='풍향', values='갯수', title='풍향계급별 분포',
    #              hover_data=['풍향', '갯수'])
    # fig.update_traces(textposition='inside', textinfo='percent+label')
    #
    # return fig
    df['풍향'] = df['풍향'].apply(lambda x: text_to_degrees(x))
    grouped_data = df.groupby('풍향').size().reset_index(name='갯수')
    fig = px.bar_polar(grouped_data, r='갯수', theta='풍향', title='풍향계급별 분포')
    fig.update_traces(marker=dict(color='blue'))
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction='clockwise',
                period=360
            )
        )
    )
    return fig


def show_df(minute_df, hour_df):
    show_cols = ['datetime', 'temp', 'hum', 'rad', 'wd', 'ws', 'rain', 'maxws']
    show_minute = copy.deepcopy(minute_df)
    show_minute = show_minute[show_cols]

    show_hour = copy.deepcopy(hour_df)
    show_hour = show_hour[show_cols]



def main():
    folder_path = "./output/AWS"

    min_date, max_date1, max_date2 = min_max_date(folder_path)

    col1, col2 = st.columns(2)

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Select a start date", min_value=min_date, max_value=max_date1, value=min_date,
                                   key=1)
        start_date_str = start_date.strftime('%Y%m%d')

    with col2:
        end_date = st.date_input("Select an end date", min_value=min_date, max_value=max_date2, value=max_date2, key=2)
        end_date_str = end_date.strftime('%Y%m%d')

    minute_df, hour_df = aws2summary.get_dataframe(start_date_str, end_date_str, folder_path)
    daily_df, wd_category = aws2summary.daily_data(minute_df, hour_df)
    dates_df = aws2summary.weekly_date(daily_df)

    daily_df['폭염일수'] = daily_df['폭염일수'].apply(lambda x: '-' if x == 0 else x)
    daily_df['강수일수'] = daily_df['강수일수'].apply(lambda x: '-' if x == 0 else x)
    daily_df['한파일수'] = daily_df['한파일수'].apply(lambda x: '-' if x == 0 else x)

    # 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다.
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Day Vis', 'Daily Vis', 'Summary Table', 'Hour Table', 'Minute Table'])

    with tab1:
        select_date = st.date_input("Select an end date", min_value=start_date, max_value=end_date, value=end_date,
                                    key=3)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        chart_selection = st.radio("Select a chart:", ["온습도", "온도", "습도"], key="chart_selection")

        day_temphumid = day_temphumid_line(minute_df, select_date)
        selected_chart = st.plotly_chart(day_temphumid)

        if chart_selection == "온습도":
            selected_chart.plotly_chart(day_temphumid)
        elif chart_selection == "온도":
            selected_chart.plotly_chart(day_temp_line(minute_df, select_date))
        elif chart_selection == "습도":
            selected_chart.plotly_chart(day_humid_line(minute_df, select_date))

        day_rad = day_rad_line(minute_df, select_date)
        st.plotly_chart(day_rad)

    with tab2:
        week_temp = week_temp_line(minute_df)
        st.plotly_chart(week_temp)

        daily_tempdiff = daily_tempdiff_line(daily_df)
        st.plotly_chart(daily_tempdiff)

        daily_temprain = daily_temprain_linebar(daily_df)
        st.plotly_chart(daily_temprain)

        rain_pie = rain_count_pie(daily_df)
        st.plotly_chart(rain_pie)

        wd_pie = wd_count_pie(wd_category)
        st.plotly_chart(wd_pie)

    with tab3:
        st.write('요약 통계')
        st.write(daily_df)

        st.write(dates_df)

        st.write('풍향 계급')
        wd_category = wd_category.groupby(['date'])['풍향'].value_counts().reset_index(name='counts')
        wd_category = wd_category.pivot(index='date', columns='풍향', values='counts')
        wd_category = wd_category.fillna(0)
        st.write(wd_category)

    with tab4:

        show_hour_df = hour_df[['datetime', 'temp', 'hum', 'rad', 'wd', 'ws', 'rain', 'maxws', 'bv']]
        st.write(show_hour_df)

    with tab5:

        number = st.number_input("분 간격 입력", min_value=0, max_value=55, value=10, step=5)

        show_minute_df = minute_df[['datetime', 'temp', 'hum', 'rad', 'wd', 'ws', 'rain', 'maxws', 'bv']]
        show_minute_df = show_minute_df[show_minute_df['datetime'].dt.minute % number == 0]

        st.write(show_minute_df)

if __name__ == '__main__':
    main()