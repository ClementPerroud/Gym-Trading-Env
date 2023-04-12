# Crypto-Trading-Env


<img alt="Render example" src ="https://github.com/ClementPerroud/Gym-Trading-Env/blob/main/readme_images/render.gif?raw=true" width = "800"/>

An OpenAI Gym environment for simulating stocks and train Reinforcement Learning (RL) trading agents.

Designed to be **FAST** and **CUSTOMIZABLE** for easy RL trading algorythms implementation.
## Install and import
```pip install gym-trading-env```

Then import :

```python
from gym_trading_env.environments import TradingEnv
```

## Environment Properties

### Actions space : positions

Github is full of environments that consider actions such as **BUY**, **SELL**. In my opinion, it is a real mistake to consider a reinforcement learning agent in the same way as a trader. Traders make trade and to do so, they place orders on the market (eg. Buy X of stock Y). But what really matter is the position reached. Now, imagine we labelled each position by a number :
- ```1``` : All of our portfolio is converted into stock Y. (=*BUY ALL*)
- ```0``` : All of our portfolio is converted into our fiat currency. (=*SELL ALL*)


Now, we can imagine half position and other variants :
- ```0.5``` : 50% in stock Y & 50% in currency
- Even : ```0.1``` : 10% in stock Y & 90% in currency
....


In fact, it is way simpler for a RL-agent to work with positions. This way, it can easily make complex operation with a simple action space.

But if you want to use a really basic environment, you can use only 2 positions : ```1``` and ```0``` which is more of less equivalent to **BUY ALL** and **SELL ALL** actions.

### Complex positions

This environment supports more complex positions such as:
- ```-1``` : Bet 100% of the portfolio value on the decline of asset Y (=SHORT). To perform this action, the environment borrows 100% of the portfolio valuation as stock Y to an imaginary person, and immediately sells it. When the agent closes this position, the environment buys the owed amount of stock Y and repays the imaginary person with it. If the price has fallen during the operation, we buy cheaper than we sold what we need to repay : the difference is our gain. The imaginary person is paid a small rent (parameter : ```borrow_interest_rate```)
- ```+2``` : Bet 100% of the portfolio value of the rise of asset Y. We use the same mechanism explained above, but we borrow currency and buy stock Y.
- ```-10``` ? : We can BUT ...  We need to borrow 1000% of the portfolio valuation as asset Y. You need to understand that such a "leverage" is very risky. As if the stock price rise by 10%, you need to repay the original 1000% of your portfolio valuation at 1100% (1000%*1.10) of your current portfolio valuation. Well, 100% (1100% - 1000%) of your portfolio is used to repay your debt. **GAME OVER, you have 0$ left**. The leverage is very useful but also risky, as it increases your **gains** AND your **losses**. Always keep in mind that you can lose everything.

### How to use ?

**1 - Import and clean your data**. They need to be ordered by ascending date. Index must be DatetimeIndex. Your DataFrame needs to contain a close price labelled ```close``` to run. If you want to render your results, your DataFrame needs to contain open, high, low, volume features respectively labelled ```open```, ```high```, ```low```, ```volume```.
```python
# Available in the github repo : test/data/BTC_USD-Hourly.csv
df = pd.read_csv("data/BTC_USD-Hourly.csv", parse_dates=["date"], index_col= "date")
df.sort_index(inplace= True)
df.dropna(inplace= True)
df.drop_duplicates(inplace=True)
```
**1.1 (Optional) Download data** : The package provide a easy way to download data (works with CCTX ans use asyncio to get FAST) :
```python
from gym_trading_env.downloader import download
import datetime

download(
    exchange_names = ["binance", "bitfinex2", "huobi"],
    symbols= ["BTC/USDT", "ETH/USDT"],
    timeframe= "30m",
    dir = "test/data",
    since= datetime.datetime(year= 2019, month= 1, day=1),
    until = datetime.datetime(year= 2023, month= 1, day=1),
)
```
This function use pickle format to save the OHLCV data. You will need to import the dataset with ```pd.read_pickle('... .pkl', ...)```. The function supports exchange_names ```binance```, ```biftfinex2``` (API v2) and ```huobi```.


**2 - Create your features**. Your RL-agent will need some good, preprocessed features. It is your job to make sure it has everything it needs.
**The feature column names need to contain the keyword 'feature'. The environment will automatically detect them !**

```python
df["feature_close"] = df["close"].pct_change()
df["feature_open"] = df["open"]/df["close"]
df["feature_high"] = df["high"]/df["close"]
df["feature_low"] = df["low"]/df["close"]
df["feature_volume"] = df["Volume USD"] / df["Volume USD"].rolling(7*24).max()
df.dropna(inplace= True) # Clean your data !
```
**(Optional)3 - Create your own reward function**. Use the history object described below to create your own ! For example : 
```python
import numpy as np
def reward_function(history):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )
```
The history object is similar to a DataFrame. It uses timestep and/or columns to access its values. You can use it this way :
>- ```history['column name', t]``` returns the a *scalar* value of the metrics 'column name' at time step t.
>- ```history['column name']``` returns a *numpy array* with all the values from timestep 0 to current timestep.
>- ```history[t]``` returns a *dictionnary* with of the metrics as keys with the associated values.


Accessible columns of history object :
>- ```step``` : Step = t.
>- ```date``` : Date at step t, datetime.
>- ```reward``` : Reward at step t.
>- ```position_index``` : Index of the position at step t amoung your position argument.
>- ```position``` : Portfolio position at step t.
>- ```portfolio_valuation```: Global valuation of the portfolio.
>- It gathers every data (not used as features) from your DataFrame and labels them with 'data_{column}'. For example :```data_close```, ```data_open```,  ```data_high```....
>- It stores the distribution of the portfolio : ```portfolio_distribution_asset``` the amount of owned asset (stock), ```portfolio_distribution_fiat``` the amount of owned fiat currency, ```portfolio_distribution_borrowed_asset``` amount of borrowed asset, ```portfolio_distribution_borrowed_fiat``` the amount of borrowed fiat currency, ```portfolio_distribution_interest_asset``` the total of cumalated interest generated by the borrowed asset, ```portfolio_distribution_interest_fiat``` the total of cumalated interest generated by the borrowed fiat currency.


**4 - Initiate the environment**

```python
env = TradingEnv(
        name= "BTCUSD",
        df = df,
        windows= 5,
        positions = [ -1, -0.5, 0, 0.5, 1], # From -1 (=SHORT), to +1 (=LONG)
        initial_position = 0,
        trading_fees = 0.01/100, # 0.01% per stock buy / sell (Binance fees)
        borrow_interest_rate= 0.0003/100, # 0.0003% per timestep (= 1h here)
        reward_function = reward_function,
        portfolio_initial_value = 1000, # here, in USDT
    )
```
Parameters :
>- ```name``` (required) : Name of your asset / symbol
>- ```df``` (required) : DataFrame containing technical indicators ```open```, ```high```, ```low```, ```close```, ```volume```, and the features you want to be returned as observations (containing ```feature``` in their column names).
>- ```windows```(optional, default : None), If None, observation at t are the features at step t  (classic mode). If windows = i (int),  observation at t are the features from steps [t-i+1 :  t] (useful for reccurent models)
>- ```positions``` (optional, default : [0, 1]). Positions that the agent can choose (Explained in "Actions space : positions")
>- ```initial_position``` (optional, default : 0). Initial position of the portfolio
>- ```trading_fees``` (optional, default : 0). Trading fee for buy and sell.
>- ```borrow_interest_rate``` (optional, default : 0). Borrow interest rate PER STEP.
>- ```reward_function``` (Optional, default : the reward function used above). Reward function.
>- ```portfolio_initial_value``` (optional, default : 1000). Initial value of the portfolio (in FIAT currency)

**5 - Run the environment**
```python
truncated, done = False, False
observation, info = env.reset()
while not truncated and not done:
    action = env.action_space.sample()
    observation, reward, done, truncated, info = env.step(action)
```
>- ```observation``` : Returns a dict with items :
>    - ```features``` : Contains the features created. If windows is None, it contains the features of the current step (shape = (n_features,)). If windows is i (int), it contains the features the last i steps (shape = (5, n_features)).
>    - ```position``` : The last position of the environments. It can be useful to include this to the features, so the agent knows which position it is.
>- ```reward``` : The step reward following the action taken.
>- ```done```: Always False.
>- ```truncated``` : is true if the end of the DataFrame is reached.
>- ```info``` : Returns the last history step of the object "history" presented above (in "3 - Create your own reward function")


### 6 - Render performed with Flask (local app).

<img alt="Render example" src ="https://github.com/ClementPerroud/Gym-Trading-Env/blob/main/readme_images/render.gif?raw=true" width = "800"/>

For the render not to perturb the training, it needs to be performed in a separate python script. This way you have plenty of time to perform analysis on your results. 

First, you need to save your results at the end of every episode you want to render with ```env.save_for_render(...)```. And decide which file you want your logs to be stored in with paramter ```dir```. For example :

```python
...
# At the end of the episode you want to render
env.save_for_render(dir = "render_logs")
```

Then in the separated render script. You can import and initiate a renderer object, and run the render in a localhost web app :
```python
from gym_trading_env.renderer import Renderer
renderer = Renderer(render_logs_dir="render_logs")
renderer.run()
```
#### Custom render

You can add **metrics** and plot **lines** with :
```python
renderer = Renderer(render_logs_dir="render_logs")

# Add Custom Lines (Simple Moving Average)
renderer.add_line( name= "sma10", function= lambda df : df["close"].rolling(10).mean(), line_options ={"width" : 1, "color": "purple"})
renderer.add_line( name= "sma20", function= lambda df : df["close"].rolling(20).mean(), line_options ={"width" : 1, "color": "blue"})

# Add Custom Metrics (Annualized metrics)
renderer.add_metric(
    name = "Annual Market Return",
    function = lambda df : f"{ ((df['close'].iloc[-1] / df['close'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
)

renderer.add_metric(
        name = "Annual Portfolio Return",
        function = lambda df : f"{((df['portfolio_valuation'].iloc[-1] / df['portfolio_valuation'].iloc[0])**(pd.Timedelta(days=365)/(df.index.values[-1] - df.index.values[0]))-1)*100:0.2f}%"
)

renderer.run()
```

<img alt="Render example" src ="https://github.com/ClementPerroud/Gym-Trading-Env/blob/main/readme_images/render_customization.gif?raw=true" width = "800"/>



>```.add_line``` takes arguments :
>- ```name``` (*required*): The name of the scatter
>- ```function``` (*required*): The function used to compute the line. The function must take an argument ```df``` which is a DateFrame and return a Series, 1D-Array or list.
>- ```line_options``` : Can contain a dict with keys ```color``` and ```width```
>
>
>```.add_metric``` takes arguments :
>- ```name``` : The name of the metric
>- ```function``` : The function used to compute the line. The function must take an argument ```df``` which is a DateFrame and return a **string** !


Enjoy :)




