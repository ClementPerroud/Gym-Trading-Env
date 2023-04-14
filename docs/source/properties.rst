Environment properties
==================

Actions space : positions
---------------------------

Github is full of environments that consider actions such as BUY, SELL. In my opinion, it is a real mistake to consider a reinforcement learning agent in the same way as a trader. Traders make trade and to do so, they place orders on the market (eg. Buy X of stock Y). But what really matter is the position reached. Now, imagine we labelled each position by a number :

* 1 : All of our portfolio is converted into stock Y. (=BUY ALL)
* 0 : All of our portfolio is converted into our fiat currency. (=SELL ALL)
Now, we can imagine half position and other variants :

* 0.5 : 50% in stock Y & 50% in currency
* Even : 0.1 : 10% in stock Y & 90% in currency ....
In fact, it is way simpler for a RL-agent to work with positions. This way, it can easily make complex operation with a simple action space.

But if you want to use a really basic environment, you can use only 2 positions : 1 and 0 which is more of less equivalent to BUY ALL and SELL ALL actions.

Complex positions
-----------------

This environment supports more complex positions such as:

* -1 : Bet 100% of the portfolio value on the decline of asset Y (=SHORT). To perform this action, the environment borrows 100% of the portfolio valuation as stock Y to an imaginary person, and immediately sells it. When the agent closes this position, the environment buys the owed amount of stock Y and repays the imaginary person with it. If the price has fallen during the operation, we buy cheaper than we sold what we need to repay : the difference is our gain. The imaginary person is paid a small rent (parameter : borrow_interest_rate)
* +2 : Bet 100% of the portfolio value of the rise of asset Y. We use the same mechanism explained above, but we borrow currency and buy stock Y.
* -10 ? : We can BUT ... We need to borrow 1000% of the portfolio valuation as asset Y. You need to understand that such a "leverage" is very risky. As if the stock price rise by 10%, you need to repay the original 1000% of your portfolio valuation at 1100% (1000%*1.10) of your current portfolio valuation. Well, 100% (1100% - 1000%) of your portfolio is used to repay your debt. GAME OVER, you have 0$ left. The leverage is very useful but also risky, as it increases your gains AND your losses. Always keep in mind that you can lose everything.
