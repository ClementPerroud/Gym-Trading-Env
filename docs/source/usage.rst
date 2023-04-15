Usage
===================

Action spaces
----------------------

Positions
~~~~~~~~~~

I have seen many environments that consider actions such as BUY, SELL. In my experience, it is a mistake to consider a reinforcement learning agent in the same way as a trader. Because, behind a trade, what really matter is the : **position reached**. In the environment, we label each position by a number :
*example with pair BTC/USDT*

* ``1`` : All of our portfolio is converted into BTC. **(=BUY ALL)**
* ``0`` : All of our portfolio is converted into USDT. **(=SELL ALL)**
*Now, we can imagine half position and other variants :*

* ``0.5`` : 50% in BTC & 50% in USDT
* Even : ``0.1`` : 10% in BTC & 90% in USDT ....
In fact, it is way simpler for a RL-agent to work with positions. This way, it can easily make complex operation with a simple action space.

.. code-block::python
  
    positions = [0, 0.5, 1]
    #... environment has been initialized with your positions list on pair BTC/USDT
    _ = env.step(1)
    # You just told the environment the reached the position : positions[1] = 0.5 ! The environment manages the trades to reach this 50% BTC, 50% USDT
 

Complex positions
~~~~~~~~~~

This environment supports more complex positions such as:

* ``-1`` : Bet 100% of the portfolio value on the decline of BTC (=SHORT). To perform this action, the environment borrows 100% of the portfolio valuation as stock Y to an imaginary person, and immediately sells it. When the agent closes this position, the environment buys the owed amount of stock Y and repays the imaginary person with it. If the price has fallen during the operation, we buy cheaper than we sold what we need to repay : the difference is our gain. The imaginary person is paid a small rent (parameter : borrow_interest_rate).
* ``+2`` : Bet 100% of the portfolio value of the rise of asset Y. We use the same mechanism explained above, but we borrow currency and buy stock Y.
* ``-10`` ? : We can BUT ... We need to borrow 1000% of the portfolio valuation as asset Y. You need to understand that such a "leverage" is very risky. As if the stock price rise by 10%, you need to repay the original 1000% of your portfolio valuation at 1100% (1000%*1.10) of your current portfolio valuation. Well, 100% (1100% - 1000%) of your portfolio is used to repay your debt. GAME OVER, you have 0$ left. The leverage is very useful but also risky, as it increases your gains AND your losses. Always keep in mind that you can lose everything.


Import your data
-------------------


They need to be ordered by ascending date. Index must be DatetimeIndex. Your DataFrame needs to contain a close price labelled ``close``for the environment to run, and open, high, low, volume features respectively labelled ``open``, ``high``, ``low``, ``volume`` to perform renders.

.. code-block:: python

  # Available in the github repo : test/data/BTC_USD-Hourly.csv
  df = pd.read_csv("data/BTC_USD-Hourly.csv", parse_dates=["date"], index_col= "date")
  df.sort_index(inplace= True)
  df.dropna(inplace= True)
  df.drop_duplicates(inplace=True)
  
The packaging also include an easy way to download historical data of crypto pairs. Its stores data as .pkl for easy usage and fast reading. 

.. code-block:: python

  from gym_trading_env.downloader import download
  import datetime
  import pandas as pd
  
  # Download BTC/USDT historical data from Binance and stores it to directory ./data/binance-BTCUSDT-1h.pkl
  download(exchange_names = ["binance"],
      symbols= ["BTC/USDT"],
      timeframe= "1h",
      dir = "data",
      since= datetime.datetime(year= 2020, month= 1, day=1),
  )
  # Import your fresh data
  df = pd.read_pickle("./data/binance-BTCUSDT-1h.pkl")



