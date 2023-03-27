# Crypto-Trading-Env

An OpenAI Gym environment for simulating stocks and train Reinforcement Learning trading agents.

Designed to be FAST and CUSTOMIZABLE for an easy RL implementation.

## Environment Properties

# Actions space

Github is full of environments that consider actions such as *BUY*, *SELL*. And to me, it is a really mistake to think a RL-agent as a trader. Traders make trade and to do so, they place orders on the market (eg. Buy X of stock Y). But what really matter is the position reached. For example, a trader that sell half of his stocks Y, wants to reduce his risk, but also his potential gains. Now, image we labelled each position by a number going with:
- 1 : We have bought as much as possible of stock Y (LONG); ideally, we have all of our stock's portfolio converted in the stock Y
- 0 : We have sold as much as possible of stock Y (OUT); ideally, we have all of our stock's portfolio converted in our currency
Now, we can imagine half position or others :
- 0.5 : 50% in stock Y & 50% in currency
- 0.1 : 10% in stock Y & 90% in currency

In fact, it is way simpler for a RL-agent to work with position. This way, it can easily make complex operation with a simple action space.
Plus, this environment supports more complex positions such as:
- -1 : bet 100% of the portfolio value against the asset Y
