import sys  
sys.path.append("./")

from src.gym_trading_env.renderer import Renderer

renderer = Renderer(

)


renderer.add_scatter("sma10", lambda df : df["close"].rolling(10).mean(),
        scatter_args = {
            "line": {"color":'blue'}
        },
        secondary_y = False)
renderer.add_scatter("sma40", lambda df : df["close"].rolling(40).mean(),
        scatter_args = {
            "line": {"color": "purple"}
        },
        secondary_y = False)

def drawdown(df):
    current_max = df["portfolio_valuation"].iloc[0]
    max_drawdown = 0
    for i in range(len(df)):
        current_max = max(df["portfolio_valuation"].iloc[i], current_max)
        max_drawdown = min(max_drawdown, (df["portfolio_valuation"].iloc[i] - current_max)/current_max)
    return f"{max_drawdown*100:0.2f}%"

renderer.add_metric("Max drawdown", drawdown)
renderer.run()