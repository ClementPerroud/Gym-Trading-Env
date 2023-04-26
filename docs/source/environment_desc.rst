Quick summary
============

.. image:: images/render.gif
  :width: 600
  :align: center
  
This environment is a `Gymnasium <https://gymnasium.farama.org/content/basic_usage/>`_ environment made for trading.

.. list-table:: Title
   :widths: 25 70
   :header-rows: 0
   
   * - Action Space
     - ``Discrete( number_of_positions )``
   * - Observation Space
     - ``Box( -np.inf, +np.inf, shape = ...)``
   * - Import
     - ``gymnasium.make("TradingEnv", df = df)``

Important Parameters
--------------------

* ``df`` *(required)*: A pandas.DataFrame with a ``close`` and DatetimeIndex as index. To perform a render, your DataFrame also needs to contain ``open`` , ``low`` , ``high``. 
* ``positions`` *(optional, default : [-1, 0, 1])* : The list of positions that your agent can take. Each position is represented by a number (as described in section *Action Space*).

`Documentation of all the parameters <https://gym-trading-env.readthedocs.io/en/latest/documentation.html#gym_trading_env.environments.TradingEnv>`_

Action Space
-----------

The action space is a list of **position** given by the user. Every position is labelled from -inf to +inf and corresponds to the ratio of the porfolio valuation engaged in the position ( > 0 to bet on the rise, < 0 to bet on the decrease).

Some examples on BTC/USDT pair (%pv means *"Percent of the Portfolio Valuation"*):

* 0 : 0%pv in BTC, 100%pv in USDT
* 1 : 100%pv in BTC, 0%pv in USDT
* 0.5 : 50%pv in BTC, 50%pv in USDT
* 2 : 200%pv in BTC, 0%pv in USDT, 100%pv borrowed of USDT (Margin trading)
* -1 : 0%pv in BTC, 200%pv in USDT, 100%pv borrowed of BTC (Short)

If ``position < 0`` : the environment performs a SHORT (by borrowing USDT and buying BTC with it).

If ``position > 1`` : the environment uses MARGIN trading (by borrowing BTC and selling it to get USDT).

Observation Space
------------------

The obersation space is a np.array containing:

* The row of your DataFrame columns containing ``features`` in their name, at a given step.
* The current position of the environment to allow self-awareness for the agent. You can disable it by setting ``include_position_in_features`` to ``False`` .

.. code-block:: python

  >>> # df is a DataFrame containing open, high, low, close, volume columns with a DatetimeIndex index.
  >>> df["feature_pct_change"] = df["close"].pct_change()
  >>> df["feature_high"] = df["high"] / df["close"] - 1
  >>> df["feature_low"] = df["low"] / df["close"] - 1
  >>> df.dropna(inplace= True)
  >>> env = gymnasium.make("TradingEnv", df = df, positions = [-1, 0, 1], initial_position= 1)
  >>> observation, info = env.reset()
  >>> observation
  array([-0.00120265,  1.0024953 ,  0.992214  ,  1.        ], dtype=float32)
