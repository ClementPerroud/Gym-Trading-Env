from gymnasium.envs.registration import register

register(
    id='TradingEnv',
    entry_point='gym_trading_env.environments:TradingEnv',
    disable_env_checker = True,
    order_enforce= False
)
register(
    id='MultiDatasetTradingEnv',
    entry_point='gym_trading_env.environments:MultiDatasetTradingEnv',
    disable_env_checker = True,
    order_enforce= False
)
 