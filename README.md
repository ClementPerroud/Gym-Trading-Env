# Crypto-Trading-Env

An OpenAI Gym environment for simulating stocks and train Reinforcement Learning trading agents.

Designed to be **FAST** and **CUSTOMIZABLE** for an easy RL trading algorythms implementation.

## Environment Properties

### Actions space

Github is full of environments that consider actions such as **BUY**, **SELL**. And to me, it is a really mistake to think a RL-agent as a trader. Traders make trade and to do so, they place orders on the market (eg. Buy X of stock Y). But what really matter is the position reached. For example, a trader that sell half of his stocks Y, wants to reduce his risk, but also his potential gains. Now, image we labelled each position by a number going with:
>- ```1``` : We have bought as much as possible of stock Y (LONG); ideally, we have all of our stock's portfolio converted in the stock Y
>- ```0``` : We have sold as much as possible of stock Y (OUT); ideally, we have all of our stock's portfolio converted in our currency
Now, we can imagine half position or others :
>- ```0.5``` : 50% in stock Y & 50% in currency
>- ```0.1``` : 10% in stock Y & 90% in currency

In fact, it is way simpler for a RL-agent to work with position. This way, it can easily make complex operation with a simple action space.
Plus, this environment supports more complex positions such as:
>- ```-1``` : once every stock Y is sold, we bet 100% of the portfolio value on the decline of asset Y. To perform this action, the environments borrows 100% of the portfolio valuation as stock Y to a imaginary person, and immediatly sell it. When the agent closes the position (position 0), the environment buys the owed amount of stock Y and repays the imaginary person with it. If the price have fallen during the operation, we buy cheaper than we sold what we need to repay : the difference is our gain. The imaginary person is paid a small rent (parameter : ```borrow_interest_rate```)
>- ```+2``` : buy as much stock as possible, then we bet 100% of the portfolio value of the rise of asset Y. We use the same mecanism explained abose, but we borrows currency and buy stock Y.
> ```-10``` ? : We can !  We need to borrow 1000% of the portfolio valuation as asset Y. But you need to understand that such a "leverage" is very risky. As if the stock price rise by 10%, you need to repay the original 1000% of your portfolio valuation at 1100% portfolio valuation. Well, 100% (1100 - 1000) of your portfolio is used to repay your debt. **GAME OVER, you have 0$ left**. The leverage is very usely but also risky, as it increases your **gains** AND your **losses**. Always keep in mind that you can lose everything.

### How to use ?
