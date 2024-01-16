import os
import pytz
import pandas as pd

import streamlit as st
from streamlit_option_menu import option_menu

import load
import show

seoul = pytz.timezone('Asia/Seoul')
aws_dir = './output/AWS'
daily_dir = './output/daily'
def show_fig(fig):
    st.plotly_chart(fig, use_container_width = True)

def current_menu():
    kind = 'current'
    df = load.today_data()
    show.current_block(df)
    show.select_fig(df, kind)


def past_menu():
    kind = 'week'
    sd, ed = show.select_sd_ed(kind)
    df = load.past_data(sd, ed)
    show.select_fig(df, kind)
    show.table(df, kind)


def summary_menu():
    sd, ed = show.select_sd_ed('summary')
    df = load.summary_data(sd, ed)
    st.write(df)

def main():
    choice = option_menu(None, ["Today", "Past", "Summary"],
                         icons=['bi-clock', 'calendar4-range', 'bi-clipboard-data', 'database-down'],
                         menu_icon="cast", default_index=0, orientation="horizontal")

    if choice == 'Today':
        current_menu()
    elif choice == 'Past':
        past_menu()
    elif choice == 'Summary':
        summary_menu()

if __name__ == '__main__':
    main()