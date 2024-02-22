import pandas as pd
import datetime as dt
from datetime import datetime


def datedelta_to_minutes(datedelta):
    days, seconds = datedelta.days, datedelta.seconds
    minutes = days * 24 * 60 + (seconds // 60)
    return minutes


def ISO_string_to_datetime(s):
    return datetime.fromisoformat(s).replace(tzinfo=None)


def lable_week_and_month(df, date_keyword):
    df[date_keyword] = pd.to_datetime(df[date_keyword])
    df['year'] = df[date_keyword].dt.year
    df['month'] = df[date_keyword].dt.month
    df['month_label'] = ''
    df['week'] = df[date_keyword].dt.isocalendar().week
    df['week_label'] = ''
    df[date_keyword] = df[date_keyword].dt.date

    current_year = dt.date.today().isocalendar().year
    current_month = datetime.now().month
    current_week = dt.date.today().isocalendar().week

    df.loc[(df['year'] == current_year) & (df['month'] == current_month), 'month_label'] = '本月'
    df.loc[(df['year'] == current_year) & (df['week'] == current_week), 'week_label'] = '本周'

    last_week = dt.date.today() - dt.timedelta(days=7)
    df.loc[(df['year'] == last_week.year) & (df['week'] == last_week.isocalendar().week), 'week_label'] = '上周'

    if current_month == 1:
        df.loc[(df['year'] == current_year - 1) & (df['month'] == 12), 'month'] = '上月'
    else:
        df.loc[(df['year'] == current_year) & (df['month'] == current_month - 1), 'month_label'] = '上月'

    return df





