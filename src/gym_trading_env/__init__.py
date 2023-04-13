from gymnasium.envs.registration import register

register(
    id='TradingEnv',
    entry_point='gym_trading_env.environments:TradingEnv'
)
register(
    id='MultiDatasetTradingEnv',
    entry_point='gym_trading_env.environments:MultiDatasetTradingEnv'
)
 