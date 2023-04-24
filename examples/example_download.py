import sys  
sys.path.append("./src")


from gym_trading_env.downloader import download, EXCHANGE_LIMIT_RATES
import datetime

EXCHANGE_LIMIT_RATES["bybit"] = {
    "limit":200, # One request will query 1000 data points (aka candlesticks)
    "pause_every": 120, # it will pause every 10 request
    "pause" : 2, # the pause will last 1 second
}
download(
    exchange_names = ["bybit"],
    symbols= ["BTC/USDT", "ETH/USDT"],
    timeframe= "1h",
    dir = "examples/data",
    since= datetime.datetime(year= 2023, month= 1, day=1),
)