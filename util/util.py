import pandas as pd


def export_to_excel(df, filename):
    with pd.ExcelWriter(filename, engine="xlsxwriter",
                        datetime_format="mmm d yyyy hh:mm:ss",
                        date_format="yyyy-mm-dd") as writer:
        df.to_excel(writer, index=False)