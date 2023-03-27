import pandas as pd
import numpy as np
from environments import TradingEnv
import time

# Import your datas
df = pd.read_csv("data/BTC-Hourly.csv", parse_dates=["date"], index_col= "date")
df.sort_index(inplace= True)

# Generating features
# WARNING : the column names need to contain keyword 'feature' !
df["feature_close"] = df["close"].pct_change()
df["feature_open"] = df["open"]/df["close"]
df["feature_high"] = df["high"]/df["close"]
df["feature_low"] = df["low"]/df["close"]
df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
df.dropna(inplace= True)

df["close"] = 1000

# Create your own reward function with the history object
def reward_function(history):
    return np.log(history[-1]["portfolio_info"]["value"] / history[-2]["portfolio_info"]["value"]) #log (p_t / p_t-1 )

env = TradingEnv(
        df = df,
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
    action = env.action_space.sample()
    observation, reward, done, truncated, info = env.step(action)


# Render
env.render()