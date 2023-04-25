Vectorize your env
=================

You still want your agent to perform better ?

Then, I suggest to use Vectorized Environment to parallelize several environments. It garanties having multiple simultaneous sources of data during the training.

.. code-block:: python

  import gymnasium as gym
  import gym_trading_env
  
  >>>envs = gym.vector.make(
  >>>  "MultiDatasetTradingEnv",
  >>>  dataset_dir = "preprocessed_data",
  >>>  num_envs = 3)
  >>>envs.reset()
  (array([[-1.06232299e-03,  1.00112247e+00,  1.00135887e+00,
         9.99291003e-01,  4.42897417e-02,  0.00000000e+00],
       [ 1.77242109e-04,  9.99822795e-01,  1.00023627e+00,
         9.99291182e-01,  2.12742039e-03,  0.00000000e+00],
       [ 1.18140466e-04,  9.99940932e-01,  1.00005901e+00,
         9.99350309e-01,  4.57133725e-03,  0.00000000e+00],
       [ 3.54379532e-04,  9.99586701e-01,  1.00000000e+00,
         9.99409556e-01,  1.54840061e-02,  0.00000000e+00],
       [-5.90423333e-05,  1.00000000e+00,  1.00029528e+00,
         9.99940932e-01,  3.08786577e-04,  0.00000000e+00]], dtype=float32), {'step': 5, 'date': numpy.datetime64('2023-01-08T04:00:00.000000000'), 'position_index': 2, 'position': 0, 'data_close': 16936.0, 'data_high': 16941.0, 'data_open': 16936.0, 'data_low': 16935.0, 'data_volume': 0.03704266, 'data_date_close': Timestamp('2023-01-08 05:00:00'), 'portfolio_valuation': 1000.0, 'portfolio_distribution_asset': 0, 'portfolio_distribution_fiat': 1000.0, 'portfolio_distribution_borrowed_asset': 0, 'portfolio_distribution_borrowed_fiat': 0, 'portfolio_distribution_interest_asset': 0, 'portfolio_distribution_interest_fiat': 0, 'reward': 0})
  
    
