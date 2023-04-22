import gymnasium as gym
from gymnasium import spaces
import pandas as pd
import numpy as np
import datetime
import glob
from pathlib import Path    

from collections import Counter
from .utils.history import History
from .utils.portfolio import Portfolio, TargetPortfolio

import tempfile, os
import warnings
warnings.filterwarnings("error")
def basic_reward_function(history : History):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2])

class TradingEnv(gym.Env):
    """A trading environment for OpenAI gym"""
    metadata = {'render_modes': ['human']}
    def __init__(self,
                df : pd.DataFrame,
                positions : list = [0, 1],
                reward_function = basic_reward_function,
                windows = None,
                trading_fees = 0,
                borrow_interest_rate = 0,
                max_leverage = None,
                portfolio_initial_value = 1000,
                initial_position = 0,
                include_position_in_features = True,
                verbose = 1,
                name = "Stock",
                ):
        self.name = name
        self.verbose = verbose

        self.positions = positions
        self.reward_function = reward_function
        self.windows = windows
        self.trading_fees = trading_fees
        self.borrow_interest_rate = borrow_interest_rate
        self.max_leverage =max_leverage
        self.portfolio_initial_value = float(portfolio_initial_value)
        self.initial_position = initial_position
        assert self.initial_position in self.positions, "The 'initial_position' parameter must one position mentionned in the 'position' (default is [0, 1]) parameter."
        self.include_position_in_features = include_position_in_features
        self._set_df(df)
        

        self.action_space = spaces.Discrete(len(positions))
        self.observation_space = spaces.Box(
            -np.inf,
            np.inf,
            shape = [self._nb_features]
        )
        if self.windows is not None:
            self.observation_space = spaces.Box(
                -np.inf,
                np.inf,
                shape = [self.windows, self._nb_features]
            )


    def _set_df(self, df):
        df = df.copy()
        self._features_columns = [col for col in df.columns if "feature" in col]
        self._info_columns = list(set(list(df.columns) + ["close"]) - set(self._features_columns))
        self._nb_features = len(self._features_columns)

        if self.include_position_in_features:
            df["feature_position"] = self.initial_position
            self._features_columns.append("feature_position")
            self._nb_features += 1
        self.df = df
        self._obs_array = np.array(self.df[self._features_columns], dtype= np.float32)
        self._info_array = np.array(self.df[self._info_columns])
        self._price_array = np.array(self.df["close"])

    
    def _get_ticker(self, delta = 0):
        return self.df.iloc[self._step + delta]
    def _get_price(self, delta = 0):
        return self._price_array[self._step + delta]
    
    def _get_obs(self):
        if self.include_position_in_features: self._obs_array[self._step, -1] = self._position
        if self.windows is None:
            _step_index = self._step
        else: 
            _step_index = np.arange(self._step + 1 - self.windows , self._step + 1)
        return self._obs_array[_step_index]

    
    def reset(self, seed = None, options=None):
        super().reset(seed = seed)
        self._step = 0
        self._limit_orders = {}
        if self.windows is not None: self._step = self.windows

        self._portfolio  = TargetPortfolio(
            position=self.initial_position,
            value= self.portfolio_initial_value,
            price = self._get_price()
        )
        self._position = self.initial_position
        self.historical_info = History(max_size= len(self.df))
        self.historical_info.set(
            step = self._step,
            date = self.df.index.values[self._step],
            action = self.positions.index(self.initial_position),
            position = self._position,
            data =  dict(zip(self._info_columns, self._info_array[self._step])),
            portfolio_valuation = self.portfolio_initial_value,
            portfolio_distribution = self._portfolio.get_portfolio_distribution(),
            reward = 0,
        )

        return self._get_obs(), self.historical_info[0]

    def _trade(self, position, price = None):
        self._portfolio.trade_to_position(
            position, 
            price = self._get_price() if price is None else price, 
            trading_fees = self.trading_fees
        )
        self._position = position
        return

    def _take_action(self, position):
        if position != self._position:
            self._trade(position)
    
    def _take_action_order_limit(self):
        if len(self._limit_orders) > 0:
            ticker = self._get_ticker()
            for position, params in self._limit_orders.items():
                if position != self._position and params['limit'] <= ticker["high"] and params['limit'] >= ticker["low"]:
                    self._trade(position, price= params['limit'])
                    if not params['persistent']: del self._limit_orders[position]


    
    def add_limit_order(self, position, limit, persistent = False):
        self._limit_orders[position] = {
            'limit' : limit,
            'persistent': persistent
        }
    
    def step(self, position_index = None):
        if position_index is not None: self._take_action(self.positions[position_index])
        self._step += 1

        self._take_action_order_limit()
        price = self._get_price()
        self._portfolio.update_interest(borrow_interest_rate= self.borrow_interest_rate)
        portfolio_value = self._portfolio.valorisation(price)
        portfolio_distribution = self._portfolio.get_portfolio_distribution()
        done, truncated = False, False
        if portfolio_value <= 0: done = True
        if self._step >= len(self.df) - 1:
            truncated = True
        
        self.historical_info.add(
            step = self._step,
            date = self.df.index.values[self._step],
            action = position_index,
            position = self._position,
            data =  dict(zip(self._info_columns, self._info_array[self._step])),
            portfolio_valuation = portfolio_value,
            portfolio_distribution = portfolio_distribution, 
            reward = 0
        )
        if not done:
            reward = self.reward_function(self.historical_info)
            self.historical_info["reward", -1] = reward

        if done or truncated: self.render(self.historical_info)
        return self._get_obs(),  self.historical_info["reward", -1], done, truncated, self.historical_info[-1]
    
    def render(self, history):
        if self.verbose > 0:
            market_return = history["data_close", -1] / history["data_close", 0] -1
            portfolio_return = history["portfolio_valuation", -1] / history["portfolio_valuation", 0] -1
            sharpe_ratio = (portfolio_return - 0.04) / np.std(history["portfolio_valuation"])
            nb_positions = (np.diff(history["position"])!= 0).sum(axis=0)

            print(f"""Market Return : {100*market_return:5.2f}%   |   Portfolio Return : {100*portfolio_return:5.2f}%   |   Sharpe Ratio : {100*sharpe_ratio:4.2f}   |   Positions : {nb_positions:3d} """)
        
    def save_for_render(self, dir = "render_logs"):
        assert "open" in self.df and "high" in self.df and "low" in self.df and "close" in self.df, "Your DataFrame needs to contain columns : open, high, low, close to render !"
        columns = list(set(self.historical_info.columns) - set([f"date_{col}" for col in self._info_columns]))
        history_df = pd.DataFrame(
            self.historical_info[columns], columns= columns
        )
        history_df.set_index("date", inplace= True)
        history_df.sort_index(inplace = True)
        render_df = self.df.join(history_df, how = "inner")
        
        if not os.path.exists(dir):os.makedirs(dir)
        render_df.to_pickle(f"{dir}/{self.name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl")

class MultiDatasetTradingEnv(TradingEnv):
    def __init__(self, dataset_dir, preprocess, *args, **kwargs):
        self.dataset_dir = dataset_dir
        self.preprocess = preprocess
        self.dataset_pathes = glob.glob(self.dataset_dir)
        self.dataset_nb_uses = np.zeros(shape=(len(self.dataset_pathes), ))
        super().__init__(self.next_dataset(), *args, **kwargs)

    def next_dataset(self):
        # Find the indexes of the less explored dataset
        potential_dataset_pathes = np.where(self.dataset_nb_uses == self.dataset_nb_uses.min())[0]
        # Pick one of them
        random_int = np.random.randint(potential_dataset_pathes.size)
        dataset_path = self.dataset_pathes[random_int]
        self.dataset_nb_uses[random_int] += 1 # Update nb use counts

        self.name = Path(dataset_path).name
        return self.preprocess(pd.read_pickle(dataset_path))

    def reset(self, seed=None):
        self._set_df(
            self.next_dataset()
        )
        if self.verbose > 1: print(f"Selected dataset {self.name} ...")
        return super().reset(seed)
    
