Usage
===================

Action spaces
----------------------

Positions
~~~~~~~~~~

I have seen many environments that consider actions such as BUY, SELL. In my experience, it is a mistake to consider a reinforcement learning agent in the same way as a trader. Because, behind a trade, what really matter is the : **position reached**. In the environment, we label each position by a number :
*(example with pair BTC/USDT)*

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


Create your features
-------------------

Your RL-agent will need inputs. It is your job to make sure it has everything it needs. 
> **The environment will recognize as inputs every column that contains the keyword 'feature' in its name.**

.. code-block:: python

  # df is a DataFrame with columns : "open", "high", "low", "close", "Volume USD"
  
  # Create the feature : ( close[t] - close[t-1] )/ close[t-1]
  df["feature_close"] = df["close"].pct_change() 
  
  # Create the feature : open[t] / close[t]
  df["feature_open"] = df["open"]/df["close"]
  
  # Create the feature : high[t] / close[t]
  df["feature_high"] = df["high"]/df["close"]
  
  # Create the feature : low[t] / close[t]
  df["feature_low"] = df["low"]/df["close"]
  
   # Create the feature : volume[t] / max(*volume[t-7*24:t+1])
  df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
  
  df.dropna(inplace= True) # Clean again !
  # Eatch step, the environment will return 5 inputs  : "feature_close", "feature_open", "feature_high", "feature_low", "feature_volume"
  
  
Create your reward function
-------------------

Use the history object to create your custom reward function. Bellow is an example with a really basic reward function :math:`ln(\frac{p_{t}}{p_{t-1}})\text{ with }p_{t}\text{ = portofolio valuation at timestep }t`. More information about the history object here... (Coming soon)

.. code-block:: python
  
  import numpy as np
  def reward_function(history):
      return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2])


Create your first environment
-------------------

Well done, you did a good job configuring your fist environment !

.. code-block:: python

  import gymnasium as gym
  env = gym.make("TradingEnv",
          name= "BTCUSD",
          df = df, # Your dataset with your custom features 
          positions = [ -1, 0, 1], # -1 (=SHORT), 0(=OUT), +1 (=LONG)
          trading_fees = 0.01/100, # 0.01% per stock buy / sell (Binance fees)
          borrow_interest_rate= 0.0003/100, # 0.0003% per timestep (one timestep = 1h here)
          reward_function = reward_function # Your custom reward function
      )
  
Run the environment
-------------------

Now it's time to enjoy.

.. code-block:: python
 
  # Run an episode until it ends :
  done, truncated = False, False
  observation, info = env.reset()
  while not done and not truncated:
      # Pick a position by its index in your position list (=[-1, 0, 1])....usually something like : position_index = your_policy(observation)
      position_index = env.action_space.sample() # At every timestep, pick a random position index from your position list (=[-1, 0, 1])
      
      observation, reward, done, truncated, info = env.step(position_index)
      

