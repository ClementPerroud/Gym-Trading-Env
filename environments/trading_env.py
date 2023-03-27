import gym
from gym import spaces
import pandas as pd
import numpy as np
from collections import Counter
from environments.renderer import CandleStickRenderer


import warnings
warnings.filterwarnings("error")


class TradingEnv(gym.Env):
    """A trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}
    def __init__(self,
                df : pd.DataFrame,
                positions : list = [0, 1],
                reward_function = lambda info : np.log(1 + info[-1]["portfolio_info"]["value"] / info[-2]["portfolio_info"]["value"]),
                windows = None,
                fees = 0,
                max_leverage = None,
                portfolio_initial_value = 1000,
                initial_position = 0,
                ):
        self._set_df(df)
        self.positions = positions
        self.reward_function = reward_function
        self.windows = windows
        self.fees = fees
        self.max_leverage =max_leverage
        self.portfolio_initial_value = float(portfolio_initial_value)
        self.initial_position = initial_position

        self.action_space = spaces.Discrete(len(positions))
        self.observation_space = spaces.Dict(
            {
                "features": spaces.Box(
                    self._obs_array.min(),
                    self._obs_array.max(),
                    shape = (self._nb_features, self.windows) if self.windows is not None else (self._nb_features, )
                ),
                "position": spaces.Box(-1, 1)
            }
        )
        self.renderer = None

    def _set_df(self, df):
        self._features_columns = [col for col in df.columns if "feature" in col]
        self._info_columns = list(set(list(df.columns) + ["close"]) - set(self._features_columns))
        self._nb_features = len(self._features_columns)

        self.df = df
        self._obs_array = np.array(self.df[self._features_columns])
        self._info_array = np.array(self.df[self._info_columns])
        self._price_array = np.array(self.df["close"])
    def _get_price(self, delta = 0): return self._price_array[self._step + delta]
    def _get_portfolio_value(self): return  self._portfolio["asset"] * self._get_price() + self._portfolio["fiat"]
    def _generate_portfolio(self, position, portfolio_value):
        return {
            "asset": position * portfolio_value / self._get_price(),
            "fiat": (1 - position) * portfolio_value
        }
    def _leverage_check(self, portfolio_repartition):
        if (portfolio_repartition["borrowed_asset"] * self._get_price() + portfolio_repartition["borrowed_fiat"]) > 0.95*self.max_leverage * (portfolio_repartition["asset"] * self._get_price() + portfolio_repartition["fiat"]):
            return True
        return False
    
    def _get_portfolio_repartition(self):
        return {
            "asset":max(0, self._portfolio["asset"]),
            "fiat":max(0, self._portfolio["fiat"]),
            "borrowed_asset":max(0, -self._portfolio["asset"]),
            "borrowed_fiat":max(0, -self._portfolio["fiat"])
        } 
    def _get_obs(self):
        if self.windows is None: _step_index = self._step
        else: _step_index = np.arange(self._step + 1 - self.windows , self._step + 1)
        return {
            "features" : self._obs_array[_step_index],
            "position" : self._position
            }
    
    def reset(self, seed = None, df = None):
        super().reset(seed = seed)
        if df is not None: self._set_df(df)
        self._step = 0
        if self.windows is not None: self._step = self.windows

        self._portfolio  = self._generate_portfolio(self.positions[self.initial_position], self.portfolio_initial_value)
        self._position = self.positions[self.initial_position]
        self.historical_info = [{
            "step": self._step,
            "date":self.df.index.values[self._step],
            "reward":0,
            "position_index": self.initial_position,
            "position" : self.positions[self.initial_position],
            "pair_info": dict(zip(self._info_columns, self._info_array[self._step])),
            "portfolio_info":{
                "value" : self.portfolio_initial_value,
                "repartition": self._get_portfolio_repartition()
            } 
        }]
        return self._get_obs(), self.historical_info[0]
    
    def _trade(self, position):
        old_position = self._position
        if position * old_position < 0:
            self._trade(0)
            old_position = 0

        target_portfolio = self._generate_portfolio(position, self._get_portfolio_value())

        fee_factor = 1
        if position <= 0 and old_position <= 0 < 0: fee_factor = 1/(1 - self.fees)
        asset_mouvement = {asset:(target_portfolio[asset] - self._portfolio[asset])*fee_factor for asset in target_portfolio.keys()} 

        asset_fees = {asset : mouvement * self.fees if mouvement > 0 else 0 for asset, mouvement in asset_mouvement.items()}
        self._portfolio = {asset:self._portfolio[asset] + asset_mouvement[asset] - asset_fees[asset] for asset in target_portfolio.keys()}

    def _take_action(self, position):
        if position != self._position:
            self._trade(position)
            self._position = position
                    
    
    def step(self, position_index):
        self._take_action(self.positions[position_index])
        self._step += 1

        portfolio_value = self._get_portfolio_value()
        portfolio_repartion = self._get_portfolio_repartition()
        

        done, truncated = False, False
        if self.max_leverage is not None:
            done = self._leverage_check(portfolio_repartion)
        if self._step >= len(self.df) - 1:
            truncated = True
        
        self.historical_info.append({
            "step": self._step,
            "date":self.df.index.values[self._step],
            "position_index": position_index,
            "position" : self.positions[position_index],
            "pair_info": dict(zip(self._info_columns, self._info_array[self._step])),
            "portfolio_info":{
                "value" : portfolio_value,
                "repartition": portfolio_repartion
            } 
        })
        reward = self.reward_function(self.historical_info)
        self.historical_info[-1]["reward"] = reward
        return self._get_obs(),  self.reward_function(self.historical_info), done, truncated, self.historical_info[-1]
    
    def render(self):
        assert "open" in self.df and "high" in self.df and "low" in self.df and "close" in self.df, "Your DataFrame needs to contain columns : open, high, low, close to render !"
        history = [[
                self.historical_info[i]["date"],
                self.historical_info[i]["position"], # action
                self.historical_info[i]["reward"], # action
                self.historical_info[i]["portfolio_info"]["value"], # portfolio_value
            ] for i in range(len(self.historical_info))
        ]
        history_df = pd.DataFrame(history)
        history_df.columns = ["date", "action", "reward", "portfolio_value"]
        render_df = self.df.join(history_df.set_index("date"), how = "inner")

        if self.renderer is None:
            self.renderer = CandleStickRenderer(render_df)
            self.renderer.run()
        else:
            self.renderer.update_df(render_df)

    
