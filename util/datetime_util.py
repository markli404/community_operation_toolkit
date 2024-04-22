import pandas as pd
import datetime as dt
from datetime import datetime
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

def datedelta_to_minutes(datedelta):
    days, seconds = datedelta.days, datedelta.seconds
    minutes = days * 24 * 60 + (seconds // 60)
    return minutes


def ISO_string_to_datetime(s):
    if s.endswith('Z'):
        s = s[:-1]
    return datetime.fromisoformat(s).replace(tzinfo=None)


def generate_index(some_list):
    prev = some_list[0]
    index = 1
    for i in range(len(some_list)):
        if prev != some_list[i]:
            index += 1
            prev = some_list[i]
        some_list[i] = index
    return some_list

def lable_week_and_month(df, date_keyword, name_keyword='name'):
    df[date_keyword] = pd.to_datetime(df[date_keyword])
    res = []
    def generate_week_and_month_label(df):
        df = df.sort_values(by=date_keyword)
        df[date_keyword] = pd.to_datetime(df[date_keyword])

        month = df[date_keyword].dt.month.tolist()
        week = df[date_keyword].dt.isocalendar().week.tolist()

        # generate week index
        df['week'] = generate_index(week)
        df['month'] = generate_index(month)

        df['week_label'] = ''
        df['month_label'] = ''

        df[date_keyword] = df[date_keyword].dt.date
        df.loc[df['month'] == max(df['month']), 'month_label'] = '本月'
        df.loc[df['month'] == (max(df['month']) - 1), 'month_label'] = '上月'

        df.loc[df['week'] == max(df['week']), 'week_label'] = '本周'
        df.loc[df['week'] == (max(df['week']) - 1), 'week_label'] = '上周'

        return df

    if name_keyword is not None:
        for name in df[name_keyword].unique():
            df_by_name = df[df[name_keyword] == name]
            res.append(generate_week_and_month_label(df_by_name))

        df = pd.concat(res)
        return df

    else:
        return generate_week_and_month_label(df)








