import pandas as pd
import numpy as np

from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


class CandleStickRenderer():
    def __init__(self, df, n_candles = 1000, reward_smoothing = 20):
        self.n_candles = n_candles
        self.reward_smoothing = reward_smoothing
        self.update_df(df)

    def update_df(self, df):
        self.df = df
        self.df.sort_index(inplace= True)
        self.df["date_str"] = self.df.index.to_series().apply(lambda x: x.strftime("%b. %Y"))
        self.df["smoothed_reward"] = self.df["reward"].rolling(self.reward_smoothing).mean()

        self.df.dropna(inplace=True)

    def run(self):
        self.app = Dash(__name__)
        
        self.app.layout = html.Div([
            html.H2('Stock candlestick chart'),
            dcc.Graph(
                id="graph_candlestick",
            ),
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
            ], style = {"display": "block", "width": "1100px"})
        ], style={"display":"flex", "flexDirection":"column", "alignItems":"center", "fontFamily": '"Open Sans", verdana, arial, sans-serif'}
        )

        @self.app.callback(
            Output("graph_candlestick", "figure"), 
            Input('date-slider', 'value'))
        def display_candlestick(i):
            i = min(i, len(self.df) - self.n_candles)
            temp_df = self.df.iloc[0+i:self.n_candles+i].copy()

            fig = make_subplots(rows=4, cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.10,
                                row_heights=[0.55, 0.15, 0.15, 0.15],
                                subplot_titles=('Price evolution',  'Agent action', 'Portfolio valuation', f'N-{self.reward_smoothing}-Smoothed reward')
                                )
            
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

            mask = temp_df["action"]> 0
            x = temp_df.index.to_numpy()
            actions = temp_df["action"].to_numpy()
            fig.add_trace(
                go.Scatter(x=x, y = actions, fill="tozeroy", mode='lines',fillcolor = "rgba(169,196,242,0.5)", line=dict(width=1,color="rgba(169,196,242,0.8)")),
                row=2,
                col=1
            )


            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["portfolio_value"], mode = None, line=dict(width=1, color='rgba(255,242,0,1)'),),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["smoothed_reward"], mode = None, line=dict(width=1, color='blue'),),
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
            return fig
        self.app.run_server(debug=True)