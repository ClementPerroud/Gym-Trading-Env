import pandas as pd
import numpy as np
import datetime

from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import glob

class Renderer():
    def __init__(self, render_dir = "render_logs", reward_smoothing = 20):
        self.reward_smoothing = reward_smoothing
        self.render_dir = "render_logs"
        self.scatters = []
        self.scatter_key = "9882290544"
        self.metrics = [
            {"name": "Market Return", "function": lambda df : f'{100*df["close"].iloc[-1]/df["close"].iloc[0]:0.2f}%'},
            {"name": "Portfolio Return", "function": lambda df : f'{100*df["portfolio_valuation"].iloc[-1]/df["portfolio_valuation"].iloc[0]:0.2f}%'}
        ]
    def add_scatter(self, name, function, secondary_y = False, scatter_args = None):
        self.scatters.append({"name": name, "function": function, "secondary_y" : secondary_y, "scatter_args": scatter_args})
    def add_metric(self, name, function):
        self.metrics.append({"name": name, "function":function})
    def update_list_df(self):
        self.pathes = glob.glob(f"{self.render_dir}/*.pkl")
    def update_df(self, path):
        self.df_path = path
        self.df = pd.read_pickle(path)
        self.df.sort_index(inplace= True)
        self.df["date_str"] = self.df.index.to_series().apply(lambda x: x.strftime("%b. %Y"))
        self.df["smoothed_reward"] = self.df["reward"].rolling(self.reward_smoothing).mean()

        for scatter in self.scatters:
            self.df[self.scatter_key + scatter["name"]] = scatter["function"](self.df)
        for metric in self.metrics:
            metric["value"] = metric["function"](self.df)

        self.position_df = self.df[["position"]].copy()
        new_position_df = self.position_df.copy()
        new_position_df.index += datetime.timedelta(microseconds=1)
        new_position_df["position"] = np.nan
        self.position_df = pd.concat([new_position_df, self.position_df])
        self.position_df.sort_index(inplace=True)
        self.position_df.fillna(method="bfill",inplace=True)
        self.position_df.dropna(inplace=True)
        self.df.dropna(inplace=True)
        print(self.df.columns)

    def run(self):
        self.update_list_df()
        self.update_df(self.pathes[0])

        self.app = Dash(__name__)
        self.app.layout = html.Div([
            html.Div([
                html.H2('Stock candlestick chart'),
                dcc.Graph(
                    id="graph_candlestick",
                ),
                html.H3("Parameters"),
                html.Span("Render selector", style = {"color":"darkgrey"}),
                dcc.Dropdown(self.pathes, self.pathes[0], id='df-selector-dropdown', style = {"width": "700px"}),
                html.Span("Date selector", style ={"color":"darkgrey", "marginTop": "10px"}),
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
                ], style = {"display": "block", "width": "800px"}),
                html.Span("Number of candles", style ={"color":"darkgrey", "marginTop": "10px"}),
                html.Div([
                    dcc.Slider(
                        1,
                        np.log10(len(self.df)-100),
                        value= 2, step = 0.01,
                        marks = {i : f"{10**i}" for i in range(2, 1 +int(np.log10(len(self.df)-100)))},
                        id='candle-slider',
                    )
                ], style = {"display": "block", "width": "800px"}),
                html.Div(id='updatemode-output-container', style={'margin-top': "20px", "color":"darkgrey"})
            ], style={"display":"flex", "flexDirection":"column", "alignItems":"center"}),
            html.Div([
                html.H2("Metrics"),
                html.Div([
                    html.Div([
                        html.H4(metric["name"], style = {"margin-bottom":"10px"}),
                        html.Span(metric["value"])
                    ]) for metric in self.metrics
                ],style = {"display": "flex", "width": "350px", "justify-content":"center", "gap":"20px", "flex-wrap": "wrap"})
            ],style= {"align-self": "start", "text-align":"center"}),
        ], style={"display":"flex", "alignItems":"center","justify-content": "center", "gap": "30px", "fontFamily": '"Open Sans", verdana, arial, sans-serif'})

        @self.app.callback(
            Output("graph_candlestick", "figure"),
            Output('updatemode-output-container', 'children'),
            Input('date-slider', 'value'),
            Input('candle-slider', 'value'),
            Input('df-selector-dropdown', 'value'))
        def display_candlestick(i, k, df_path):
            if df_path != self.df_path:
                self.update_df(df_path)
            n_candles = int(10**k)
            i = min(i, len(self.df) - n_candles)
            temp_df = self.df.iloc[0+i:n_candles+i].copy()
            temp_position_df = self.position_df.loc[temp_df.index.values[0]:temp_df.index.values[-1]].copy()

            height_size = np.array([1, 0.4, 0.4, 0.4, 0.4])
            fig = make_subplots(rows=5, cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.10,
                                row_heights= list(height_size / np.sum(height_size)),
                                subplot_titles=('Price evolution',  'Volume', 'Portfolio position', 'Portfolio valuation', f'N-{self.reward_smoothing}-Smoothed reward')
                                )
            row = 1
            # Candlesticks
            if n_candles <= 1000:
                fig.add_trace(
                    go.Candlestick(
                        x=temp_df.index,
                        open=temp_df['open'],
                        high=temp_df['high'],
                        low=temp_df['low'],
                        close=temp_df['close'],
                        increasing_line_color= '#28e19d', decreasing_line_color="#e64d48"
                    ),row=row, col=1
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=temp_df.index,
                        y=temp_df['close'],
                        mode = "lines",
                        line= dict(color='blue'),
                    ),row=row, col=1
                )

            # Custom Scatters
            for scatter in self.scatters:
                print(scatter)
                fig.add_trace(
                    go.Scatter(
                        x=temp_df.index,
                        y = temp_df[self.scatter_key + scatter["name"]],
                        **scatter["scatter_args"]   
                    ), row = row, col = 1
                )
            row += 1
            # Volume plot
            temp_df["close_diff"] = temp_df["close"].diff()
            pos_volume_df = temp_df.loc[temp_df["close_diff"] >= 0, "volume"]
            neg_volume_df = temp_df.loc[temp_df["close_diff"] < 0, "volume"]
            fig.add_trace(
                go.Bar(
                    x = pos_volume_df.index,
                    y = pos_volume_df,
                    marker={
                        "color": "rgba(0, 255, 0 ,0.5)",
                    }
                ), row = 2, col = 1
            )
            fig.add_trace(
                go.Bar(
                    x = neg_volume_df.index,
                    y = neg_volume_df,
                    marker={
                        "color": "rgba(255, 0, 0 ,0.5)",
                    }
                ), row = row, col = 1
            )
            # Positions taken
            row += 1           
            fig.add_trace(
                go.Scatter(x=temp_position_df.index, y = temp_position_df["position"], fill="tozeroy", mode='lines',fillcolor = "#a3b0ff", line=dict(width=0.5,color="blue")),
                row=row,
                col=1
            )
            # Portfolio evolution
            row += 1
            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["portfolio_valuation"], line=dict(width=1, color='blue'),),
                row=row,
                col=1,
            )
            # Rewards
            row += 1
            fig.add_trace(
                go.Scatter(x=temp_df.index, y = temp_df["smoothed_reward"], fill="tozeroy", fillcolor="#a3b0ff", line=dict(width=1, color='blue'),),
                row=row,
                col=1,
            )
            fig.update_layout(
                height=100 + row * 200, 
                width=800,
                xaxis_rangeslider_visible=False,
                margin = dict(t=20, b=10, l = 20, r = 20),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="darkgrey",
                yaxis = dict(fixedrange=True, showgrid=False,),
                yaxis2 = dict(fixedrange=True, showgrid=False,), # Position
                yaxis3 = dict(fixedrange=True, range = [self.df["position"].min(), self.df["position"].max()], showgrid=False,),
                yaxis4 = dict(fixedrange=True, showgrid=False,),
                yaxis5 = dict(fixedrange=True, showgrid=False,),
                xaxis = dict(spikemode='across+marker', showgrid=False,),    
            )
            fig.update_traces(xaxis="x1")
            return fig, f"Displaying from {temp_df.iloc[0].name.strftime('%Y/%m/%d, %r')} to {temp_df.iloc[-1].name.strftime('%m/%d/%Y, %r')} with {n_candles} candlesticks"
        self.app.run_server(debug=False)