import pandas as pd
import numpy as np
import datetime

from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


class CandleStickRenderer():
    def __init__(self, df, reward_smoothing = 20):
        self.reward_smoothing = reward_smoothing
        self.update_df(df)

    def update_df(self, df):
        self.df = df.copy()
        self.df.sort_index(inplace= True)
        self.df["date_str"] = self.df.index.to_series().apply(lambda x: x.strftime("%b. %Y"))
        self.df["smoothed_reward"] = self.df["reward"].rolling(self.reward_smoothing).mean()
        self.action_df = self.df[["action"]].copy()
        new_action_df = self.action_df.copy()
        new_action_df.index += datetime.timedelta(microseconds=1)
        new_action_df["action"] = np.nan
        self.action_df = pd.concat([new_action_df, self.action_df])
        self.action_df.sort_index(inplace=True)
        self.action_df.fillna(method="bfill",inplace=True)
        self.action_df.dropna(inplace=True)


        self.df.dropna(inplace=True)

    def run(self):
        self.app = Dash(__name__)
        
        self.app.layout = html.Div([
            html.H2('Stock candlestick chart'),
            dcc.Graph(
                id="graph_candlestick",
            ),
            html.H3("Parameters"),
            html.Span("Date selector", style ={"color":"darkgrey"}),
            html.Div([
                dcc.Slider(
                    0,
                    len(self.df)-1,
                    value= 0,
                    step= 10,
                    marks = {int(i):self.df["date_str"].iat[int(i)] for i in np.linspace(0, len(self.df)-1, 10)},
                    id='date-slider',
                    updatemode='drag'
                )
            ], style = {"display": "block", "width": "1100px"}),
            html.Span("Number of candles", style ={"color":"darkgrey"}),
            html.Div([
                dcc.Slider(
                    1,
                    np.log10(len(self.df)-100),
                    value= 2, step = 0.01,
                    marks = {i : f"{10**i}" for i in range(2, 1 +int(np.log10(len(self.df)-100)))},
                    id='candle-slider',
                )
            ], style = {"display": "block", "width": "1100px"}),
            html.Div(id='updatemode-output-container', style={'margin-top': 20, "color":"darkgrey"})
        ], style={"display":"flex", "flexDirection":"column", "alignItems":"center", "fontFamily": '"Open Sans", verdana, arial, sans-serif'}
        )

        @self.app.callback(
            Output("graph_candlestick", "figure"),
            Output('updatemode-output-container', 'children'),
            Input('date-slider', 'value'),
            Input('candle-slider', 'value'))
        def display_candlestick(i, k):
            n_candles = int(10**k)
            i = min(i, len(self.df) - n_candles)
            temp_df = self.df.iloc[0+i:n_candles+i].copy()
            temp_action_df = self.action_df.loc[temp_df.index.values[0]:temp_df.index.values[-1]].copy()

            fig = make_subplots(rows=4, cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.10,
                                row_heights=[0.55, 0.15, 0.15, 0.15],
                                subplot_titles=('Price evolution',  'Portfolio position', 'Portfolio valuation', f'N-{self.reward_smoothing}-Smoothed reward')
                                )
            if n_candles <= 1000:
                fig.add_trace(
                    go.Candlestick(
                        x=temp_df.index,
                        open=temp_df['open'],
                        high=temp_df['high'],
                        low=temp_df['low'],
                        close=temp_df['close'],
                        increasing_line_color= '#28e19d', decreasing_line_color="#e64d48"
                    ),row=1, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=temp_df.index,
                        y=temp_df['close'],
                        mode = "lines",
                        line= dict(color='blue'),
                    ),row=1, col=1
                )

            fig.add_trace(
                go.Scatter(x=temp_action_df.index, y = temp_action_df["action"], fill="tozeroy", mode='lines',fillcolor = "#a3b0ff", line=dict(width=0.5,color="blue")),
                row=2,
                col=1
            )
            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["portfolio_value"], line=dict(width=1, color='blue'),),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["smoothed_reward"], fill="tozeroy", fillcolor="#a3b0ff", line=dict(width=1, color='blue'),),
                row=4,
                col=1,
            )
            fig.update_layout(
                height=900, 
                width=1100,
                xaxis_rangeslider_visible=False,
                margin = dict(t=20, b=10, l = 20, r = 20),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="darkgrey",
                yaxis = dict(fixedrange=True, showgrid=False,),
                yaxis2 = dict(fixedrange=True, range = [self.df["action"].min(), self.df["action"].max()], showgrid=False,), # Position
                yaxis3 = dict(fixedrange=True, showgrid=False,),
                yaxis4 = dict(fixedrange=True, showgrid=False,),
                xaxis = dict(spikemode='across+marker', showgrid=False,),

                
            )
            fig.update_traces(xaxis="x1")
            return fig, f"Displaying from {temp_df.iloc[0].name.strftime('%Y/%m/%d, %r')} to {temp_df.iloc[-1].name.strftime('%m/%d/%Y, %r')} with {n_candles} candlesticks"
        self.app.run_server(debug=True)