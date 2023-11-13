import os
import pytz
import numpy as np
import pandas as pd
import urllib.request
from datetime import datetime, timedelta

import streamlit as st
from streamlit_option_menu import option_menu

import draw_figs
import aws2dataframe


seoul = pytz.timezone('Asia/Seoul')

def show_fig(fig):
    st.plotly_chart(fig, use_container_width = True)

def show_table(df, kind=None):
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

def show_select_fig(df, kind):

    fig_temphumid = draw_figs.draw_mix_line(df, '온습도', kind)
    fig_temp = draw_figs.draw_line(df, 'temp', '온도(℃)', kind)
    fig_humid = draw_figs.draw_line(df, 'hum', '습도(%)', kind)
    fig_VPD = draw_figs.draw_line(df, 'VPD', 'VPD(kPa)', kind)
    fig_cumsumrad = draw_figs.draw_line(df, 'cumsum_rad', '누적일사(MJ/m²)', kind)

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    chart_selection = st.radio("Select a chart:", ["온습도", "온도", "습도", "VPD", "누적일사"], key=f"{kind}_chart_selection")

    # selected_chart = st.plotly_chart(fig_temphumid, use_container_width = True)
    #
    # if chart_selection == "온습도":
    #     selected_chart.plotly_chart(fig_temphumid, use_container_width = True)
    # elif chart_selection == "온도":
    #     selected_chart.plotly_chart(fig_temp, use_container_width = True)
    # elif chart_selection == "습도":
    #     selected_chart.plotly_chart(fig_humid, use_container_width = True)
    # elif chart_selection == "누적광량":
    #     selected_chart.plotly_chart(fig_cumsumrad, use_container_width = True)

    # selected_chart = show_fig(fig_temphumid)

    if chart_selection == "온습도":
        show_fig(fig_temphumid)
    elif chart_selection == "온도":
        show_fig(fig_temp)
    elif chart_selection == "습도":
        show_fig(fig_humid)
    elif chart_selection == "VPD":
        show_fig(fig_VPD)
    elif chart_selection == "누적일사":
        show_fig(fig_cumsumrad)

def min_max_date(folder_path):
    csv_list = os.listdir(folder_path)
    csv_list = [int(filename.split('.')[0]) for filename in csv_list]
    max_value = str(max(csv_list))
    min_value = str(min(csv_list))

    min_date = datetime(int(min_value[:4]), int(min_value[4:6]), int(min_value[6:]))
    max_date = datetime(int(max_value[:4]), int(max_value[4:6]), int(max_value[6:]))

    max_date1 = max_date - timedelta(days=5)
    max_date2 = max_date

    return min_date, max_date1, max_date2

def show_select_date(folder_path):
    min_date, max_date1, max_date2 = min_max_date(folder_path)

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Select a start date", min_value=min_date, max_value=max_date1, value=max_date1, key=1)
        start_date_str = start_date.strftime('%Y%m%d')

    with col2:
        end_date = st.date_input("Select an end date", min_value=min_date, max_value=max_date2, value=max_date2, key=2)
        end_date_str = end_date.strftime('%Y%m%d')

    select_date = st.date_input("Select a date", min_value=min_date, max_value=max_date2, value=max_date2,
                                key=3)
    select_date_str = select_date.strftime('%Y%m%d')

    return start_date, start_date_str, end_date, end_date_str, select_date, select_date_str

def tab_vis_summary(daily_df, wd_category):
    daily_tempdiff = draw_figs.draw_tempdiff_line(daily_df)
    daily_temprain = draw_figs.draw_temp_rain(daily_df)
    rain_pie = draw_figs.draw_rain_pie(daily_df)
    wd_pie = draw_figs.draw_wd_pie(wd_category)

    show_fig(daily_tempdiff)
    show_fig(daily_temprain)
    show_fig(rain_pie)
    show_fig(wd_pie)


def tab_table_summary(daily_df, dates_df, wd_category):
    st.write('요약 통계')
    st.write(daily_df)

    st.markdown('----')

    st.write(dates_df)

    st.markdown('----')

    wd_category = wd_category.groupby(['date'])['풍향'].value_counts().reset_index(name='counts')
    wd_category = wd_category.pivot(index='date', columns='풍향', values='counts')
    wd_category = wd_category.fillna(0)
    st.write(wd_category)

    explain_df = pd.read_csv('./input/요약데이터명세서.csv')

    with st.expander("AWS 요약 통계 데이터 명세서"):
        st.write(explain_df)

def show_current_data(today_df):
    def wd_cate(x):
        directions = ["북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동", "남", "남남서", "남서", "서남서", "서", "서북서", "북서",
                      "북북서"]
        index = int((x + 11.25) / 22.5) % 16
        return directions[index]

    last_data = today_df.iloc[-1]
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

def ready_dataframe(folder_path):

    start_date, start_date_str, end_date, end_date_str, select_date, select_date_str = show_select_date(folder_path)

    df = aws2dataframe.raw_dataframe(folder_path, start_date_str, end_date_str)
    select_df = aws2dataframe.select_dataframe(folder_path, start_date_str)

    daily_df, wd_cate_df = aws2dataframe.daily_data(df)
    dates_df = aws2dataframe.weekly_date(daily_df)

    daily_df['폭염일수'] = daily_df['폭염일수'].apply(lambda x: '-' if x == 0 else x)
    daily_df['강수일수'] = daily_df['강수일수'].apply(lambda x: '-' if x == 0 else x)
    daily_df['한파일수'] = daily_df['한파일수'].apply(lambda x: '-' if x == 0 else x)

    return df, daily_df, wd_cate_df, dates_df, select_df



def choice_today():
    today_df = aws2dataframe.get_today_aws()

    show_current_data(today_df)

    tab1, tab2 = st.tabs(['Vis', 'Table'])
    with tab1:
        kind = 'today'
        show_select_fig(today_df, kind)
    with tab2:
        show_table(today_df, 'today')


def choice_past(folder_path):
    df, daily_df, wd_cate_df, dates_df, select_df = ready_dataframe(folder_path)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ['Day Vis', 'Daily Vis', 'Summary Vis', 'Day Table', 'Daily Table', 'Summary Table'])

    with tab1:
        kind = 'day'
        show_select_fig(select_df, kind)

    with tab2:
        kind = 'week'
        show_select_fig(df, kind)
    with tab3:
        tab_vis_summary(daily_df, wd_cate_df)

    with tab4:
        show_table(select_df, 'select')

    with tab5:
        show_table(df, 'week')

    with tab6:
        tab_table_summary(daily_df, dates_df, wd_cate_df)


def main():
    folder_path = "./output/AWS"
    # folder_path = "C:\code\Action-AWS\output\AWS"
    st.set_page_config(layout="wide")

    with st.sidebar:
        st.write('※ Table에 마우스 커서 위치시킨 후 다운로드 버튼 누르면 csv 다운로드 가능')
        st.write('※ Table 아래의 데이터 명세서 확인')
        st.write('※ Chart에 마우스 커서 위치시키면 상세한 값 확인 가능')

        choice = option_menu("Menu", ["Today", "Past"],
                             icons=['house', 'kanban'],
                             menu_icon="app-indicator", default_index=0,
                             styles={
                                 "container": {"padding": "4!important", "background-color": "#fafafa"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                              "--hover-color": "#fafafa"},
                                 "nav-link-selected": {"background-color": "#08c7b4"},
                             }
                             )

    if choice == 'Today':
        choice_today()
    elif choice == 'Past':
        choice_past(folder_path)


if __name__ == '__main__':
    main()
