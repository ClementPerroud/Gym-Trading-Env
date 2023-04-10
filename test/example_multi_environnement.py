import sys  
sys.path.append("./src")

import pandas as pd
import numpy as np
import time
from gym_trading_env.environments import MultiDatasetTradingEnv

# Generating features
# WARNING : the column names need to contain keyword 'feature' !
def preprocess(df):
    df["feature_close"] = df["close"].pct_change()
    df["feature_open"] = df["open"]/df["close"]
    df["feature_high"] = df["high"]/df["close"]
    df["feature_low"] = df["low"]/df["close"]
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7*24).max()
    df.dropna(inplace= True)
    return df


# Create your own reward function with the history object
def reward_function(history):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )

env = MultiDatasetTradingEnv(
        dataset_dir= 'test/data/*.pkl',
        preprocess= preprocess,
        windows= 5,
        positions = [ -1, -0.5, 0, 0.5, 1, 1.5, 2], # From -1 (=full SHORT), to +1 (=full LONG) with 0 = no position
        initial_position = 0, #Initial position
        trading_fees = 0.01/100, # 0.01% per stock buy / sell
        borrow_interest_rate= 0.0003/100, #per timestep (= 1h here)
        reward_function = reward_function,
        portfolio_initial_value = 1000, # in FIAT (here, USD)
    )

# Run the simulation
truncated = False
observation, info = env.reset()
while not truncated:
    action = env.action_space.sample() #OR manually : action = int(input("Action : ")) 
    observation, reward, done, truncated, info = env.step(action)

# Render
env.save_for_render()