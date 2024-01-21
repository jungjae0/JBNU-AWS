import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
aws_dir = './output/aws'

def wd_cate(x):
    directions = ["북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동", "남", "남남서", "남서", "서남서", "서", "서북서", "북서",
                  "북북서"]
    index = int((x + 11.25) / 22.5) % 16
    return directions[index]


def current_block(df):
    '''
    df = 오늘 데이터 > 각 요소 현재 값 보여줌
    '''
    last_data = df.iloc[-1]
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("온도", f"{last_data['temp']} ℃")
    b2.metric("습도", f"{last_data['hum']} %")
    b3.metric("일사량", f"{int(last_data['rad'])} W/m²")
    b4.metric("VPD", f"{last_data['VPD']:.2f} kPa")

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("풍속", f"{last_data['ws']} m/s")
    b2.metric("풍향", f"{wd_cate(last_data['wd'])}")
    b3.metric("최대순간풍속(60초 중 최고값)", f"{last_data['maxws']} m/s")
    b4.metric("강수량", f"{last_data['rain']} mm")

def table(df, kind=None):
    df = df[['datetime', 'temp', 'hum', 'rad', 'wd', 'ws', 'rain', 'maxws', 'bv', 'cumsum_rad', 'SVP', 'VPD']]

    number = st.number_input("분 간격 입력", min_value=0, max_value=55, value=10, step=5, key=f'{kind}_number_key')
    if number != 0:
        df = df[df['datetime'].dt.minute % number == 0]
    df.columns = ['날짜', '온도', '습도', '일사', '풍향', '풍속', '강우량', '최대순간풍속(60초)', '배터리전압', '누적일사', 'SVP', 'VPD']
    df = df.reset_index(drop=True)
    st.write(df)

    explain_df = pd.read_csv('./input/AWS데이터명세서.csv')

    with st.expander("AWS 데이터 명세서"):
        st.write(explain_df)

def select_sd_ed(key):
    dates = [int(file.split('.')[0]) for file in os.listdir(aws_dir)]
    col1, col2 = st.columns(2)
    min_date = datetime(2023, 10, 1)
    max_date2 = datetime.strptime(str(max(dates)), '%Y%m%d')
    max_date1 = max_date2 - timedelta(days=1)

    with col1:
        start_date = st.date_input("Select a start date", min_value=min_date, max_value=max_date1, value=max_date1,
                                   key=f'{key}_sd')
        sd_str = start_date.strftime('%Y%m%d')

    with col2:
        end_date = st.date_input("Select an end date", min_value=min_date, max_value=max_date2, value=max_date2, key=f'{key}_ed')
        ed_str = end_date.strftime('%Y%m%d')
    return  sd_str, ed_str

def draw_line(df, value, title, kind):
    fig = go.Figure(data=[go.Scatter(x=df["datetime"], y=df[value], name=value)])
    fig.update_yaxes(title_text=f'{title}')

    if kind == 'day' or kind == 'today':
        fig.update_layout(title_text=f'{title}')
        fig.update_xaxes(title_text='시간')

    elif kind == 'week':
        fig.update_xaxes(title_text='날짜')
        fig.update_layout(title_text=f'{title} {df["datetime"].min().date()} ~ {df["datetime"].max().date()}')
        fig.update_layout(xaxis={"rangeslider": {"visible": True}, "type": "date",
                                 "range": [df["datetime"].min(), df["datetime"].max()]})
    return fig

def draw_mix_line(df, title, kind):
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["datetime"], y=df['temp'], mode='lines', name='temp', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["hum"], name='hum', mode='lines', yaxis='y2', marker=dict(color='orange')))
    fig.update_layout(yaxis=dict(title='온도(℃)'))
    fig.update_layout(yaxis2=dict(title='습도(%)', overlaying='y', side='right', showgrid=False))
    fig.update_yaxes(range=[0, 100], tick0=0, dtick=10, secondary_y=True)

    if kind == 'day' or kind == 'today':
        fig.update_xaxes(title_text='시간')
        fig.update_layout(title_text=f'{title}')


    if kind == 'week':
        fig.update_xaxes(title_text='날짜')
        fig.update_layout(title_text=f'온습도 {df["datetime"].min().date()} ~ {df["datetime"].max().date()}')
        fig.update_layout(xaxis={"rangeslider": {"visible": True}, "type": "date",
                                 "range": [df["datetime"].min(), df["datetime"].max()]})

    return fig


def show_fig(fig):
    st.plotly_chart(fig, use_container_width = True)

def select_fig(df, kind):
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    chart_selection = st.radio("Select a chart:", ["온습도", "VPD", "누적일사"], key=f"{kind}_chart_selection")
    if chart_selection == "온습도":
        show_fig(draw_mix_line(df, '온습도', kind))
    elif chart_selection == "VPD":
        show_fig(draw_line(df, 'VPD', 'VPD(kPa)', kind))
    elif chart_selection == "누적일사":
        show_fig(draw_line(df, 'cumsum_rad', '누적일사(MJ/m²)', kind))