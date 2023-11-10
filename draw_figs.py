import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


def draw_temp_rain(df):
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=df["날짜"], y=df["강수량"], name='강수량', yaxis='y2', marker=dict(color='skyblue')))

    fig.add_trace(go.Scatter(x=df["날짜"], y=df['평균기온'], name='평균기온', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df["날짜"], y=df['최저기온'], name='최저기온', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df["날짜"], y=df['최고기온'], name='최고기온', line=dict(color='red')))


    fig.update_yaxes(range=[0, 100], tick0=0, dtick=10, secondary_y=True)
    fig.update_xaxes(title_text='날짜')

    fig.update_layout(yaxis=dict(title='온도(℃)'))
    fig.update_layout(yaxis2=dict(title='강수량(mm)', overlaying='y', side='right', showgrid=False))
    fig.update_layout(title_text='온도-강수량')

    return fig

def draw_tempdiff_line(df):
    fig = go.Figure(data=[go.Scatter(x=df["날짜"], y=df['일교차'], name='일교차')])

    fig.update_layout(title_text='일교차')
    fig.update_xaxes(title_text='날짜')
    fig.update_yaxes(title_text='일교차(℃)')

    return fig


def draw_rain_pie(df):
    grouped_data = df.groupby('강수계급').size().reset_index(name='갯수')
    fig = px.pie(grouped_data, names='강수계급', values='갯수', title='강수계급별 분포',
                 hover_data=['강수계급', '갯수'])
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def text_to_degrees(text_direction):
    direction_mapping = {
        "북": 0, "북북동": 22.5, "북동": 45, "동북동": 67.5,
        "동": 90, "동남동": 112.5, "남동": 135, "남남동": 157.5,
        "남": 180, "남남서": 202.5, "남서": 225, "서남서": 247.5,
        "서": 270, "서북서": 292.5, "북서": 315, "북북서": 337.5
    }

    return direction_mapping.get(text_direction, None)

def draw_wd_pie(df):
    df['풍향'] = df['풍향'].apply(lambda x: text_to_degrees(x))
    grouped_data = df.groupby('풍향').size().reset_index(name='갯수')
    fig = px.bar_polar(grouped_data, r='갯수', theta='풍향', title='풍향계급별 분포')
    fig.update_traces(marker=dict(color='skyblue'))
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                direction='clockwise',
                period=360
            )
        )
    )
    return fig