Multi datasets environment
==========================

Now, you know how to create an environment for your RL agent with one dataset. But something seems weird ... One good dataset is about 100k data points long. But it sounds very little compared to the millions steps that RL-Agent needs to get good.

**Is ONE SINGLE dataset enough for an agent to learn real stuff ?**

In my opinion, one dataset is not enough. The agent will overfit and won't be able to generalize. My solution is simple, adding multiple datasets to the environment. I present you the *MultiDatasetTradingEnv*.

Multi Dataset Trading Environment
---------------------------------

  (Inherits from TradingEnv)
  
A TradingEnv environment that handle multiple datasets. It automatically switches from one dataset to another at the end of an episode. Bringing diversity by having several datasets, even from the same pair from different exchanges, is a good idea. This should help avoiding overfitting.

How to use ?
^^^^^^^^^^^^

You need to specify a `glob path <https://docs.python.org/3.6/library/glob.html>`_ that gather all of the datasets (in .pkl format).
Imagine you have several preprocessed datasets in a folder named ``preprocessed_data`` .

.. code-block:: python
  
  import gymnasium as gym
  import gym_trading_env
  env = gym.make('MultiDatasetTradingEnv',
      dataset_dir = 'preprocessed_data/*.pkl',
  )

.. note::
  
    **If you do this, you need to make sure that all your datasets meets the requirements** : They need to be ordered by ascending date. Index must be DatetimeIndex. Your DataFrame needs to contain a ``close`` price labelled close for the environment to run. And open, high, low, volume columns respectively labelled ``open`` , ``high`` , ``low`` , ``volume`` to perform renders. The desired input obersations for your agent needs to contain ``feature`` in their column name).


Easy preprocess
^^^^^^^^^^^^^^^

Instead of preprocessing and saving all of your datasets every time you need to change a feature or whatever other change, I added a ``preprocess`` argument to the MultiDatasetTradingEnv. This function takes a pandas.DataFrame and returns a pandas.DataFrame. This function is applied to each dataset before it being used in the environment.

Imagine you have several raw datasets in a folder named ``raw_data`` .

.. code-block:: python

  def preprocess(df : pd.DataFrame):
    # Preprocess
    df["date"] = pd.to_datetime(df["timestamp"], unit= "ms")
    df.set_index("date", inplace = True)
    
    # Create your features
    df["feature_close"] = df["close"].pct_change()
    df["feature_open"] = df["open"]/df["close"]
    df["feature_high"] = df["high"]/df["close"]
    df["feature_low"] = df["low"]/df["close"]
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7*24).max()
    df.dropna(inplace= True)
    return df
   
  env = gym.make(
          "MultiDatasetTradingEnv",
          dataset_dir= 'raw_data/*.pkl',
          preprocess= preprocess,
      )
 
`MultiDatasetTradingEnv documentation <https://gym-trading-env.readthedocs.io/en/latest/documentation.html#gym_trading_env.environments.TradingEnv>`_ 

Run the environment
^^^^^^^^^^^^^^^^^^^

.. code-block:: python
  
  # Run 100 episodes
  for _ in range(100): 
    # At every episode, the env will pick a new dataset.
    done, truncated = False, False
    observation, info = env.reset()
    while not done and not truncated:
        position_index = env.action_space.sample() # Pick random position index
        observation, reward, done, truncated, info = env.step(position_index)

.. note::
  
  The code to run the environment does not change from ``TradingEnv``

