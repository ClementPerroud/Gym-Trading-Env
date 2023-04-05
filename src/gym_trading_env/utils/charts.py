import pyecharts.options as opts
from pyecharts.charts import Candlestick, Bar, Grid, Line
from pyecharts.components import Table
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
import numpy as np

import pandas as pd

def charts(df, lines = []):
    line_key = "ievi4G3vG678Vszad"
    for line in lines:
        df[line_key + line["name"]] = line["function"](df)
    
    df['date_str'] = df.index.strftime("%Y-%m-%d %H:%M")
    df["cumulative_rewards"] = df["reward"].cumsum()
    datas = df[["date_str", "open", "close","low","high"]].to_numpy()

    x_data = datas[:, 0].tolist()
    y_data_candles = datas[:, 1:].tolist()

    architecture = {
        "candlesticks": {"height":35, "top":10},
        "randle_slider": {"top":2},
        "volumes": {"height":9, "top":50},
        "portfolios": {"height":9, "top":63},
        "positions": {"height":9, "top":76},
        "rewards": {"height":9, "top":89},
    }
    for data in architecture.values():
        for key in list(data.keys()):data[key + "_%"] = str(data[key]) + "%"

    candlesticks = (
        Candlestick()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="",
            y_axis=y_data_candles,
            itemstyle_opts=opts.ItemStyleOpts(color="#06AF8F", color0="#FC4242", border_color="#06AF8F", border_color0="#FC4242"),
        )
        .set_series_opts()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey", position="top")
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True,
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axispointer_opts= opts.AxisPointerOpts(is_show = False),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey", position="top")

            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1, 2, 3, 4],
                    range_start=98,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1, 2, 3, 4],
                    type_="slider",
                    pos_top=architecture["randle_slider"]["top_%"],
                    range_start=95,
                    range_end=100,
                ),],
            legend_opts=opts.LegendOpts(is_show=False),
            #tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            axispointer_opts= opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": [0, 1, 2, 3, 4]}],
                    label=opts.LabelOpts(background_color="#777", is_show=False),

            ),

        ),
    )[0]
    
    line_key = "ievi4G3vG678Vszad"
    for line in lines:
        line_plot = (
            Line()
            .add_xaxis(xaxis_data= x_data)
            .add_yaxis(
                series_name=line["name"],
                y_axis= line["function"](df).tolist(),
                itemstyle_opts= opts.ItemStyleOpts(opacity=0),
                linestyle_opts= opts.LineStyleOpts(**line["line_options"]) if "line_options" in line.keys() else None,
            )
            .set_global_opts(
                xaxis_opts= opts.AxisOpts(
                    axislabel_opts= opts.LabelOpts(is_show= False),
                ),
            )
        )

        candlesticks = candlesticks.overlap(line_plot)
    
    volumes = (
        Bar()
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(
            series_name="Volume",
            y_axis=df["volume"].tolist(),
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color="blue",
                opacity = 0.3,
                border_color= "1px solid #CCCCFF",
            ),
        )
        .set_global_opts(
            xaxis_opts= opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
            ),
            yaxis_opts= opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axispointer_opts= opts.AxisPointerOpts(is_show = False),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts= opts.TitleOpts(
                is_show=True,
                title = "Volume",
                pos_top= str(architecture["volumes"]["top"] - 1) + "%",
                pos_left= "50%", text_align="center", 
                title_textstyle_opts= opts.TextStyleOpts(font_size=12, color="#adadad", font_weight=400)
            )
        )
    ,)[0]


    portfolios = (
        Line()
        .add_xaxis(xaxis_data = x_data)
        .add_yaxis(
            series_name = "Portfolio valuation",
            y_axis = df["portfolio_valuation"].tolist(),
            is_smooth=True,
            xaxis_index= 1,
            yaxis_index= 1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(color="blue",),
            markpoint_opts = opts.MarkPointOpts(symbol_size=0),
            itemstyle_opts = opts.ItemStyleOpts(opacity= 0, color="blue",border_color="blue",),
        )
        .set_global_opts(
            xaxis_opts= opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show= False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f"),
                ),
            ),
            yaxis_opts= opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axispointer_opts= opts.AxisPointerOpts(is_show = False),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts= opts.TitleOpts(
                is_show=True,
                title = "Portfolio value",
                pos_top= str(architecture["portfolios"]["top"] - 3) + "%",
                pos_left= "50%", text_align="center", 
                title_textstyle_opts= opts.TextStyleOpts(font_size='14px', color="#adadad", font_weight="400")
            )
        )
    ,)[0]
    positions = (
        Line()
        .add_xaxis(
            xaxis_data = x_data,
        )
        .add_yaxis(
            series_name = "Positions",
            y_axis = df["position"].tolist(),
            is_step = True,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(color="blue",),
            itemstyle_opts = opts.ItemStyleOpts(opacity= 0, color="blue",border_color="blue",)
        )
        .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.2, color = "blue"),
        )
        .set_global_opts(
            xaxis_opts= opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show= False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
            ),
            yaxis_opts= opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axispointer_opts= opts.AxisPointerOpts(is_show = False),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts= opts.TitleOpts(
                is_show=True,
                title = "Positions",
                pos_top= str(architecture["positions"]["top"] - 3) + "%",
                pos_left= "50%", text_align="center", 
                title_textstyle_opts= opts.TextStyleOpts(font_size='14px', color="#adadad", font_weight="400")
            )
        )
    ,)[0]


    rewards = (
        Line()
        .add_xaxis(xaxis_data = x_data)
        .add_yaxis(
            series_name = "Cumulative Rewards",
            y_axis = df["cumulative_rewards"].tolist(),
            is_smooth=True,
            xaxis_index= 1,
            yaxis_index= 1,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(color="blue",),
            markpoint_opts = opts.MarkPointOpts(symbol_size=0),
            itemstyle_opts = opts.ItemStyleOpts(opacity= 0, color="blue",border_color="blue",)
        )
        .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color = "blue"),
            label_opts=opts.LabelOpts(is_show=False),)    
        .set_global_opts(
            xaxis_opts= opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(is_show= False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
            ),
            yaxis_opts= opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(color="#ffffff1f")
                ),
                axispointer_opts= opts.AxisPointerOpts(is_show = False),
                axistick_opts= opts.AxisTickOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axisline_opts= opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0.3)),
                axislabel_opts= opts.LabelOpts(color = "grey")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            title_opts= opts.TitleOpts(
                is_show=True,
                title = "Cumulative Rewards",
                pos_top= str(architecture["rewards"]["top"] - 3) + "%",
                pos_left= "50%", text_align="center", 
                title_textstyle_opts= opts.TextStyleOpts(font_size='14px', color="#adadad", font_weight="400")
            )
        )
    ,)[0]




    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="800px",
            height="650px",
            animation_opts=opts.AnimationOpts(animation=False),
            bg_color="white",
            is_horizontal_center= True,
        )
    )

    grid_chart.add(
        candlesticks,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top= architecture["candlesticks"]["top_%"], height=architecture["candlesticks"]["height_%"]),
    )
    grid_chart.add(
        volumes,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top= architecture["volumes"]["top_%"], height=architecture["volumes"]["height_%"]
        ),
    )
    grid_chart.add(
        portfolios,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top= architecture["portfolios"]["top_%"], height=architecture["portfolios"]["height_%"]
        ),
    )
    grid_chart.add(
        positions,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top= architecture["positions"]["top_%"], height=architecture["positions"]["height_%"]
        ),
    )
    grid_chart.add(
        rewards,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top= architecture["rewards"]["top_%"], height=architecture["rewards"]["height_%"]
        ),
    )

    grid_global = Grid(
        init_opts=opts.InitOpts(
            # width="950px",
            # height="700px",
            animation_opts=opts.AnimationOpts(animation=False),
            bg_color="white",
            is_horizontal_center= True,
        )
    )
    return grid_chart
    grid_chart.render("render.html")