import sys  
sys.path.append("./src")


from gym_trading_env.downloader import download
import datetime

download(
    exchange_names = ["binance", "bitfinex2", "huobi"],
    symbols= ["BTC/USDT", "ETH/USDT"],
    timeframe= "1h",
    dir = "examples/data",
    since= datetime.datetime(year= 2019, month= 1, day=1),
)