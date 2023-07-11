import pandas as pd
from enum import Enum

from log.mixins import LoggingMixin
from log.metaclass import MethodLoggerMeta

__metaclass__ = MethodLoggerMeta


class PrintStyles(Enum):
    markdown = 0
    string = 1


class Dataframe(LoggingMixin):
    def __init__(self, csv_file, display_cols=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = self.read_into_df(csv_file)
        self.convert_to_datetime()
        self.apply_styles()
        self.display_cols = display_cols

    def __getitem__(self, i):
        return self.df[i]

    def __setitem__(self, k, v):
        self.df[k] = v

    @property
    def shape(self):
        return self.df.shape

    def read_into_df(self, csv_file):
        df = pd.read_csv(csv_file)
        return df

    def convert_to_datetime(self):
        self.df["Earning Date"] = pd.to_datetime(self.df["Earning Date"])
        self.df.sort_values(by='Earning Date', ascending=False, inplace=True)

    def apply_styles(self):
        styles = self.get_styles()
        for style in styles:
            self.df.style.applymap(style)

    def color_positive_green(self, val):
        if val > 0:
            color = 'green'
        else:
            color = 'red'
        return 'color: %s' % color

    def get_styles(self):
        return [self.color_positive_green]

    def print(self, additional_cols, style=PrintStyles.string):
        cols = self.display_cols + additional_cols
        if style == PrintStyles.markdown:
            print(self.df[cols].to_markdown())
        if style == PrintStyles.string:
            print(self.df[cols].to_string())
