Download market data
=====================

Download cryto market data
-------------------------

The package provides an easy way to download crypto market data (works with CCTX and uses asyncio for FAST download).

For exemple, this code download market data of pairs BTC/USDT, ETH/USDT with a 30 minutes timeframe, from all of the three exchanges Binance, Bitfinex and Huobi :

.. code-block:: python

  from gym_trading_env.downloader import download
  import datetime

  download(
      exchange_names = ["binance", "bitfinex2", "huobi"],
      symbols= ["BTC/USDT", "ETH/USDT"],
      timeframe= "1h",
      dir = "test/data",
      since= datetime.datetime(year= 2019, month= 1, day=1),
      until = datetime.datetime(year= 2023, month= 1, day=1),
  )

.. code-block:: bash

  BTC/USDT downloaded from binance and stored at examples/data/binance-BTCUSDT-1h.pkl
  BTC/USDT downloaded from huobi and stored at examples/data/huobi-BTCUSDT-1h.pkl
  ETH/USDT downloaded from binance and stored at examples/data/binance-ETHUSDT-1h.pkl
  ETH/USDT downloaded from huobi and stored at examples/data/huobi-ETHUSDT-1h.pkl
  BTC/USDT downloaded from bitfinex2 and stored at examples/data/bitfinex2-BTCUSDT-1h.pkl
  ETH/USDT downloaded from bitfinex2 and stored at examples/data/bitfinex2-ETHUSDT-1h.pkl

This function uses pickle format to save the OHLCV data. You will need to import the dataset with pd.read_pickle('... .pkl', ...). The function supports exchange_names binance, biftfinex2 (API v2) and huobi.
