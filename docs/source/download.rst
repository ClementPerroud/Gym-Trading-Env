Download market data
====================

Crypto market data
------------------

Supported exchanges ...
^^^^^^^^^^^^^^^^^^^^^^^

The package provides an easy way to download crypto market data (works with CCTX and uses asyncio for FAST download).

For example, this code downloads market data of pairs ``BTC/USDT`` , ``ETH/USDT`` with a 1 hour timeframe, from all of the three exchanges Binance, Bitfinex and Huobi :

.. code-block:: python

  from gym_trading_env.downloader import download
  import datetime

  download(
      exchange_names = ["binance", "bitfinex2", "huobi"],
      symbols= ["BTC/USDT", "ETH/USDT"],
      timeframe= "1h",
      dir = "data",
      since= datetime.datetime(year= 2019, month= 1, day=1),
      until = datetime.datetime(year= 2023, month= 1, day=1),
  )

Output :

.. code-block:: bash

  BTC/USDT downloaded from binance and stored at data/binance-BTCUSDT-1h.pkl
  BTC/USDT downloaded from huobi and stored at data/huobi-BTCUSDT-1h.pkl
  ETH/USDT downloaded from binance and stored at data/binance-ETHUSDT-1h.pkl
  ETH/USDT downloaded from huobi and stored at data/huobi-ETHUSDT-1h.pkl
  BTC/USDT downloaded from bitfinex2 and stored at data/bitfinex2-BTCUSDT-1h.pkl
  ETH/USDT downloaded from bitfinex2 and stored at data/bitfinex2-ETHUSDT-1h.pkl

This function uses pickle format to save the OHLCV data. You will need to import the dataset with ``pd.read_pickle('... .pkl')`` . The function supports exchange_names ``binance`` , ``bitfinex2`` (API v2) and ``huobi`` .

More exchanges ...
^^^^^^^^^^^^^^^^^^


It is possible to add other exchanges available in **ccxt**.

To do that, you need to update the ``EXCHANGE_LIMIT_RATES`` variable :

* get ``id`` of the exchange from the ccxt's list of exchanges (`available here <https://github.com/ccxt/ccxt/tree/master/python#certified-cryptocurrency-exchanges>`_).
* check the API limit rate and query policies of the exchange to complete ``limit`` , ``pause_every`` and ``pause`` parameters. Please, be kind to the APIs to avoid getting banned.

Example with **Bybit** (ccxt id : ``bybit`` ):

.. code-block:: python
  
  from gym_trading_env.downloader import download, EXCHANGE_LIMIT_RATES
  import datetime

  EXCHANGE_LIMIT_RATES["bybit"] = {
      "limit" : 200, # One request will query 200 data points (aka candlesticks).
      "pause_every" : 120, # it will pause every 120 requests.
      "pause" : 2, # the pause will last 2 seconds.
  }
  download(
      exchange_names = ["binance", "bitfinex2", "huobi", "bybit"],
      symbols= ["BTC/USDT", "ETH/USDT"],
      timeframe= "1h",
      dir = "examples/data",
      since= datetime.datetime(year= 2023, month= 1, day=1),
  )


Stock market data
-----------------

Coming soon ...
