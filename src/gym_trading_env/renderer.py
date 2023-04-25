from flask import Flask, render_template, jsonify, make_response

from pyecharts.globals import CurrentConfig
from pyecharts import options as opts
from pyecharts.charts import Bar

from .utils.charts import charts
from pathlib import Path 
import glob
import pandas as pd


class Renderer():
    def __init__(self, render_logs_dir):
        self.app = Flask(__name__, static_folder="./templates/")
        # self.app.debug = True
        self.app.config["EXPLAIN_TEMPLATE_LOADING"] = True
        self.df = None
        self.render_logs_dir = render_logs_dir
        self.metrics = [
            {
                "name": "Market Return",
                "function" : lambda df : f"{(df['close'].iloc[-1] / df['close'].iloc[0] - 1)*100:0.2f}%",
            },
            {
                "name": "Portfolio Return",
                "function" : lambda df : f"{ (df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0] - 1)*100:0.2f}%"
            },
        ]
        self.lines = []
    
    def add_metric(self, name, function):
        self.metrics.append(
            {"name": name, "function":function}
        )
    def add_line(self, name, function, line_options = None):
        self.lines.append(
            {"name": name, "function":function}
        )
        if line_options is not None: self.lines[-1]["line_options"] = line_options
    def compute_metrics(self, df):
        for metric in self.metrics:
            metric["value"] = metric["function"](df)
    def run(self,):
        @self.app.route("/")
        def index():
            render_pathes = glob.glob(f"{self.render_logs_dir}/*.pkl")
            render_names = [Path(path).name for path in render_pathes]
            return render_template('index.html', render_names = render_names)

        @self.app.route("/update_data/<name>")
        def update(name = None):
            if name is None or name == "":
                render_pathes = glob.glob(f"{self.render_logs_dir}/*.pkl")
                name = Path(render_pathes[-1]).name
            self.df = pd.read_pickle(f"{self.render_logs_dir}/{name}")
            chart = charts(self.df, self.lines)
            return chart.dump_options_with_quotes()

        @self.app.route("/metrics")
        def get_metrics():
            self.compute_metrics(self.df)
            return jsonify([{'name':metric['name'], 'value':metric['value']} for metric in self.metrics])

        self.app.run()

