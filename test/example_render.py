import sys  
sys.path.append("./")

from src.gym_trading_env.renderer import Renderer

renderer = Renderer(render_dir="render_logs")

# - Simple Moving Average - 10
renderer.add_scatter(
        name = "sma10",
        function = lambda df : df["close"].rolling(10).mean(),
        scatter_args = {
            "line": {"color":'blue'}
        })
# - Simple Moving Average - 40
renderer.add_scatter(
        name = "sma40",
        function = lambda df : df["close"].rolling(40).mean(),
        scatter_args = {
            "line": {"color": "purple"}
        })

def max_drawdown(df):
    current_max = df["portfolio_valuation"].iloc[0]
    max_drawdown = 0
    for i in range(len(df)):
        current_max = max(df["portfolio_valuation"].iloc[i], current_max)
        max_drawdown = min(max_drawdown, (df["portfolio_valuation"].iloc[i] - current_max)/current_max)
    return f"{max_drawdown*100:0.2f}%"

renderer.add_metric("Max drawdown", max_drawdown)
renderer.run()